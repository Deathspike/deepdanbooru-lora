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
        frameTagsCharacter = set(x for x in valueArray if x in tagsCharacter)
        frameTagsGeneral = set(x for x in valueArray if x in tagsGeneral)

        # Use images without character.
        if (len(frameTagsCharacter) == 0 and (
            ('1girl' in frameTagsGeneral and not '1boy' in frameTagsGeneral) or
            ('1boy' in frameTagsGeneral and not '1girl' in frameTagsGeneral))):
            # Initialize the character name.
            characterName = '1girl' if '1girl' in frameTagsGeneral else '1boy'
            imageName = os.path.splitext(textName)[0] + '.png'
            imagePath = os.path.join(config.framePath, imageName)

            # Initialize the character path.
            os.makedirs(os.path.join(config.outputPath, characterName), exist_ok=True)
            shutil.copyfile(imagePath, os.path.join(config.outputPath, characterName, imageName))

            # Write the tags.
            characterFramePath = os.path.join(config.outputPath, characterName, textName)
            valueArray = [characterName] + list(set(frameTagsGeneral))
            value = ', '.join(item.replace('_', ' ') for item in valueArray)
            with open(characterFramePath, 'w') as file: file.write(value)
