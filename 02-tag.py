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
