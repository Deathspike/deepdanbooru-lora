# Automated anime character dataset for character LoRAs

I see many people set out, desiring to train their own anime character *LoRA* for their favorite character, yet have no idea how to get started. They read tutorials, watch videos, and eventually realize that creating a data set is the foundation of training a character *LoRA*. And that the creation process is extremely tedious! I've seen many people give up because of that, but I'm here to present an alternative idea: *automate the shit out of it*. This guide gives you a deep dive into using your favorite anime as the source for your character *LoRA*.

## Requirements

You will need *ffmpeg*, the internet's favorite tool to automating anything dealing with video files, and *python*. A basic understanding of *python*, the programming language you will be using to automate tedious tasks, is recommended. It is not necessary to be an expert, but understanding enough to read and execute code snippets is fundamental.

And finally, you need the video files of your favorite anime series stored on your computer! It is essential that they do not have hardcoded subtitles, because that would interfere with training the *LoRA*. If you are not sure what hardcoded subtitles even means, try to change or disables subtitles in your video player. If you can, you're good to go~

## Keyframes and Keyframes

To train a character *LoRA*, you need images. A lot of images. And you know what? Movies are nothing more than a sequence of images to evoke the sense of movement. That means you have a lot to work with to train a *LoRA*! The basic idea here is to extract a whole lot of these images, but before you do, it is good to understand a few technical aspects of anime and video encoding.

An anime animator basically draws two types of images: keyframes and in-betweens (*tweens*). Keyframes are the most important images in anime. They show a character drawn in the way that is recognizable to the viewer, and these images show the start of a movement, the end of a movement, and the most important positions in between them. The other images, in-betweens, are just there to gradually move from one position to the other. You're interested in obtaining the keyframes since they are the most accurate. For a deeper dive into this concept, watch *Shirobako*.

In video encoding, the process of making video files as small as possible, we talk about keyframes as well. These are **not the same** as anime keyframes. This makes matters a bit confusing. I'll really simplify the concept here, but in video encoding a keyframe is essentially a full image, and each subsequent frame is *the change from the previous frame to this one*. This is not that important to remember, just know that **anime keyframes are not video keyframes**.

With all that said, it turns out that video keyframes are pretty much always on anime keyframes! That means you can simply extract video keyframes and get *mostly* anime keyframes. But even with the result being *mostly* anime keyframes, that is more than enough to train a reliable *LoRA*. Okay... that was a lot of information! Now let's go~

## Extracting Keyframes

The general idea here is to run through every anime episode and extract keyframes from all of the episodes, and write them as images to your hard disk. Depending on the anime length, the size of the output image folder can be quite large. For a 1080p anime series with 12 episodes, this easily reaches 30GB worth of images. Plan ahead and make sure you have enough disk space! Here is the *python* script to automate this process:

```py
import os
import re
import subprocess

inputPath  = '/path/to/your/anime/files'
outputPath = '/path/to/your/anime/keyframe'

for inputName in os.listdir(inputPath):
    if re.search(r'\.(avi|mp4|mkv|ogm|webm)$', inputName):
        os.makedirs(outputPath, exist_ok=True)
        videoPath = os.path.join(inputPath, inputName)
        frameName = f'{inputName}-%06d.png'
        framePath = os.path.join(outputPath, frameName)
        subprocess.run(['ffmpeg', '-i', videoPath, '-vf', 'select=eq(pict_type\\,I)', '-vsync', 'vfr', framePath], check=True)
```

This iterates through your episodes and extracts keyframes. Make sure you change `inputPath` and `outputPath` to your real folders. If you're on *Windows,* you'll need to escape backslashes (`C:\\Videos` and not `C:\Videos`). If you have an error saying *ffmpeg* can't be found, make sure you add it to *PATH*. See [How to Install FFmpeg on Windows](https://www.wikihow.com/Install-FFmpeg-on-Windows).

## Tagging Keyframes

Now that you have all the keyframes, you will need to tag them so you can easily find specific characters in the mess of tens of thousands of images. Anime models use *Booru* tags, but tagging images is tedious, time consuming, and extremely annoying. To automate this process, you can use the [DeepDanbooru](https://github.com/KichangKim/DeepDanbooru), an AI-powered image estimation system. Go download the pretrained AI model under *Releases* and extract it. Then run this in *Command Prompt* or *Terminal*:

```
pip install git+https://github.com/KichangKim/DeepDanbooru.git
pip install tensorflow tensorflow-io
```

What you're going to do now is iterate through the images and estimate the tags. These tags should be written into text files with the same name as the image (for example, `Magical Girl Lyrical Nanoha - S04E01.mkv-000007.png` will get a `Magical Girl Lyrical Nanoha - S04E01.mkv-000007.txt`). Here is the *python* script I came up with to automate this process:

```py
import deepdanbooru
import os

deepdanbooruPath = '/path/to/your/danbooru/model'
inputPath = '/path/to/your/anime/keyframe'
model = None

for i, frameName in enumerate(os.listdir(inputPath)):
    # Iterate each frame.
    print(f'{i + 1}', end='\r')
    framePath = os.path.join(inputPath, frameName)
    textName = os.path.splitext(frameName)[0] + '.txt'
    textPath = os.path.join(inputPath, textName)

    if not os.path.exists(textPath):
        # Initialize the dependencies.
        if model is None:
            # Initialize the danbooru model.
            model = deepdanbooru.project.load_model_from_project(deepdanbooruPath, compile_model=False)
            modelShape = model.input_shape

            # Initialize the danbooru tags.
            tags = deepdanbooru.project.load_tags_from_project(deepdanbooruPath)
            tagsCharacter = deepdanbooru.data.load_tags(os.path.join(deepdanbooruPath, 'tags-character.txt'))
            tagsGeneral = deepdanbooru.data.load_tags(os.path.join(deepdanbooruPath, 'tags-general.txt'))

        # Initialize the image.
        image = deepdanbooru.data.load_image_for_evaluate(framePath, width=modelShape[2], height=modelShape[1])
        imageShape = image.shape
        image = image.reshape((1, imageShape[0], imageShape[1], imageShape[2]))

        # Evaluate the image.
        result = model.predict(image)[0]
        resultCharacter = []
        resultGeneral = []

        # Initialize the image tags.
        for j, tag in enumerate(tags):
            if result[j] < 0.5:
                continue
            elif tag in tagsCharacter:
                resultCharacter.append(tag)
            elif tag in tagsGeneral:
                resultGeneral.append(tag)

        # Write the tags.
        valueArray = set(resultCharacter + resultGeneral)
        value = ', '.join(item.replace('_', ' ') for item in valueArray)
        with open(textPath, 'w') as file: file.write(value)
```

The script should be understandable enough, but this essentially iterates through your keyframes, evaluates the image with *DeepDanbooru*, and writes the tags to a text file. Make sure you change `deepdanbooruPath` and `inputPath` to your real folders. The resulting tags will not be perfect, but they will be *good enough* for training. With this step out of the way, you have a pile of images that have been tagged. This will be the basis to select character images from!

## Finding Characters

Now you're ready to find your character! At the moment of writing, the latest version of *DeepDanbooru* was trained in 2021. That means that characters that existed before that time can be found using their *character tag*. You can take a shortcut if this is the case and simply filter for the character tag, but for now, I'll explain under the assumption that your character is your seasonal *waifu* or something (but shame on you, a *waifu* is forever).

Identifying an anime character is easy. Appearances differ in all manner of things, but most characteristic are hair colors and eye colors. The idea here is to run through all the *keyframes*, look at the tags, and find something that matches your character. To find a female character with red hair, you might look for `1girl` and `red_hair`, but exclude `1boy`. If you spent some time with *Booru* tags, this will be familiar. Here is the *python* script I came up with to automate this process:

```py
import deepdanbooru
import os
import shutil

activationTag = 'waifu'
deepdanbooruPath = '/path/to/your/danbooru/model'
inputPath = '/path/to/your/anime/keyframe'
outputPath = '/path/to/your/anime/character'

tagsCharacter = deepdanbooru.data.load_tags(os.path.join(deepdanbooruPath, 'tags-character.txt'))
tagsGeneral = deepdanbooru.data.load_tags(os.path.join(deepdanbooruPath, 'tags-general.txt'))

for i, textName in enumerate(os.listdir(inputPath)):
    # Iterate each frame.
    print(f'{i + 1}', end='\r')
    textPath = os.path.join(inputPath, textName)

    if textName.endswith('.txt'):
        # Initialize the image tags.
        with open(textPath, 'r') as file: value = file.read()
        valueArray = [x.strip().replace(' ', '_') for x in value.split(',')]

        # Filter the image tags to character and general tags.
        frameCharacter = set(x for x in valueArray if x in tagsCharacter)
        frameGeneral = set(x for x in valueArray if x in tagsGeneral)

        # Find desired images.
        if ('1girl' in frameGeneral and
            '1boy' not in frameGeneral and
            'red_hair' in frameGeneral):
            # Initialize the image name.
            imageName = os.path.splitext(textName)[0] + '.png'
            imagePath = os.path.join(inputPath, imageName)

            # Initialize the image path.
            os.makedirs(outputPath, exist_ok=True)
            shutil.copyfile(imagePath, os.path.join(outputPath, imageName))

            # Write the tags.
            valueArray = [activationTag] + list(frameGeneral)
            value = ', '.join(item.replace('_', ' ') for item in valueArray)
            with open(os.path.join(outputPath, textName), 'w') as file: file.write(value)
```

Again, make sure you make sure you change `deepdanbooruPath`, `inputPath` and `outputPath`. Running this will find all the keyframes with matching tags and copy them to your `outputPath`. That will be the dataset you can train your *LoRA* on. You also want to change `activationTag` to the tag that will activate your character. I suggest you use the *Booru* tag for your character to make autocompletes work for your *LoRA*.

### Filtering

I talked about finding a girl with red hair, and that is what the previous script is doing, but you are probably not looking for a girl with red hair! You will want to look for different tags. This is where some of that *python* knowledge will become even more useful. In the aforementioned script, you can find these three lines that determine which files are copied:

```py
        if ('1girl' in frameGeneral and
            '1boy' not in frameGeneral and
            'red_hair' in frameGeneral):
```

Change this as you see fit. For example, finding a blonde girl:

```py
        if ('1girl' in frameGeneral and
            '1boy' not in frameGeneral and
            'blonde_hair' in frameGeneral):
```

Perhaps there are multiple blonde girls in the show, and the one you want has red eyes:

```py
        if ('1girl' in frameGeneral and
            '1boy' not in frameGeneral and
            'blonde_hair' in frameGeneral and
            'red_eyes' in frameGeneral):
```

Or maybe you're looking for that dashing *husbando*?Change `1girl` and `1boy` like this:

```py
        if ('1boy' in frameGeneral and
            '1girl' not in frameGeneral and
            'blonde_hair' in frameGeneral):
```

### Existing Characters

If you are looking for a character that existed back when the *DeepDanbooru* model you downloaded was trained, you might be able to the *Booru* character tag instead of filtering general tags as we have been doing so far. For example, the protagonist of the show *Magical Girl Lyrical Nanoha* has the *takamachi_nanoha* tag. I could try to look for her like this:

```py
        if ('1girl' in frameGeneral and
            '1boy' not in frameGeneral and
            'takamachi_nanoha' in frameCharacter):
```

Whether this succeeds depends on whether your character already existed, and their popularity.

## Conclusion

If you have been following along, you should have two folders. One containing all the tagged keyframes, and one containing the character images you selected for your character *LoRA*. If you plan to train more character *LoRA*s from the same show, you can continue using the keyframe folder and just use different filters to select your characters. You should take the time to look through the images in the character folder and **delete bad images and their associated text files**. If your character had enough screentime, you should have enough to work with.

### Fin

Questions? Comments? Leave them below and I'll get back to you.
