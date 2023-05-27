import config
import deepdanbooru
import os
import shutil

frameNames = os.listdir(config.framePath)
frameNamesLen = len(frameNames)
tagsCharacter = deepdanbooru.data.load_tags(os.path.join(config.deepdanbooruPath, 'tags-character.txt'))
tagsGeneral = deepdanbooru.data.load_tags(os.path.join(config.deepdanbooruPath, 'tags-general.txt'))

for i, textName in enumerate(frameNames):
    # Iterate each frame.
    print(f'{i + 1} / {frameNamesLen}', end='\r')
    textPath = os.path.join(config.framePath, textName)
    
    if textName.endswith('.txt'):
        # Initialize the image tags.
        with open(textPath, 'r') as file: value = file.read()
        valueArray = [x.strip().replace(' ', '_') for x in value.split(',')]       

        # Filter the image tags to character and general tags.
        frameTagsCharacter = [x for x in valueArray if x in tagsCharacter]
        frameTagsGeneral = [x for x in valueArray if x in tagsGeneral]

        # Use images with one character.
        if (len(frameTagsCharacter) == 1 and (
            ('1girl' in frameTagsGeneral and not '1boy' in frameTagsGeneral) or
            ('1boy' in frameTagsGeneral and not '1girl' in frameTagsGeneral))):
            tag = frameTagsCharacter[0]
            imageName = os.path.splitext(textName)[0] + '.png'
            imagePath = os.path.join(config.framePath, imageName)
            os.makedirs(os.path.join(config.outputPath, tag), exist_ok=True)
            shutil.copyfile(imagePath, os.path.join(config.outputPath, tag, imageName))

            characterFramePath = os.path.join(config.outputPath, tag, textName)
            value = ', '.join(item.replace('_', ' ') for item in [tag] + frameTagsGeneral)
            with open(characterFramePath, 'w') as file: file.write(value)
