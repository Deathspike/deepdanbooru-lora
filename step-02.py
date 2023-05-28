import config
import deepdanbooru
import os

frameNames = os.listdir(config.framePath)
frameNamesLen = len(frameNames)
model = None

for i, frameName in enumerate(frameNames):
    # Iterate each frame.
    print(f'{i + 1} / {frameNamesLen}', end='\r')
    framePath = os.path.join(config.framePath, frameName)
    textName = os.path.splitext(frameName)[0] + '.txt'
    textPath = os.path.join(config.framePath, textName)

    if not os.path.exists(textPath):
        # Initialize the dependencies.
        if model is None:
            # Initialize the danbooru model.
            model = deepdanbooru.project.load_model_from_project(config.deepdanbooruPath, compile_model=False)
            modelShape = model.input_shape

            # Initialize the danbooru tags.
            tags = deepdanbooru.project.load_tags_from_project(config.deepdanbooruPath)
            tagsCharacter = deepdanbooru.data.load_tags(os.path.join(config.deepdanbooruPath, 'tags-character.txt'))
            tagsGeneral = deepdanbooru.data.load_tags(os.path.join(config.deepdanbooruPath, 'tags-general.txt'))

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
            if result[j] < config.deepdanbooruThreshold:
                continue
            elif tag in tagsCharacter:
                resultCharacter.append(tag)
            elif tag in tagsGeneral:
                resultGeneral.append(tag)

        # Write the tags.
        valueArray = set(resultCharacter + resultGeneral)
        value = ', '.join(item.replace('_', ' ') for item in valueArray)
        with open(textPath, 'w') as file: file.write(value)
