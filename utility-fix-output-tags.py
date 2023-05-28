import config
import deepdanbooru
import os
import re

tagsGeneral = deepdanbooru.data.load_tags(os.path.join(config.deepdanbooruPath, 'tags-general.txt'))

for folderName in os.listdir(config.outputPath):
    match = re.match(r'(\d+_)?(.*)', folderName)
    if not match is None:
        characterName = match.group(2).replace('_', ' ')
        characterPath = os.path.join(config.outputPath, folderName)
        for textName in os.listdir(characterPath):
            if textName.endswith('.txt'):
                textPath = os.path.join(characterPath, textName)
                with open(textPath, 'r') as file: value = file.read()
                valueArray = [x.strip().replace(' ', '_') for x in value.split(',')]       

                frameTagsGeneral = [x for x in valueArray if x in tagsGeneral]
                desiredArray = [characterName] + frameTagsGeneral
                desiredDeduped = [x for i, x in enumerate(desiredArray) if x not in desiredArray[:i]]
                desired = ', '.join(item.replace('_', ' ') for item in desiredDeduped)

                if value != desired:
                    print(textPath)
                    with open(textPath, 'w') as file: file.write(desired)
