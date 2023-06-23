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
