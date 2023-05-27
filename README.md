# deepdanbooru-lora

A silly idea to dump and classify anime keyframes to train a stable diffusion LoRA.

## Step 0: Environment

Install `miniconda`. Then:

```
conda create -n deepdanbooru-lora python=3.10 pip
conda activate deepdanbooru-lora
pip install git+https://github.com/KichangKim/DeepDanbooru.git
pip install tensorflow tensorflow-io
```

## Step 1: Keyframe extraction

Install `ffmpeg` and edit `inputPath` and `framePath` in `config.py`. Then:

    python step-01.py

This will extract keyframes from `inputPath` and write them to `framePath`.

## Step 2: Image recognition

Download `deepdanbooru` [model](https://github.com/KichangKim/DeepDanbooru) and edit `deepdanbooruPath` in `config.py`. Then:

    python step-02.py

This will process each extracted keyframe and tag it with danbooru tags. Note you may need to update the deepdanbooru model if your characters didn't exist before the release of the deepdanbooru model (and thus cannot be tagged).

## Step 3: Image filtering

Edit `outputPath` in `config.py`. Then:

    python step-03.py

This will select keyframes matching the desired outputs. Currently this is:

    if (len(frameTagsCharacter) == 1 and ('1girl' in frameTagsGeneral and not '1boy' in frameTagsGeneral)):

Change to your desired filters. But if you're after anime girls, this will work as-is.

## Step 4: Manual work

Your screen grabs are now tagged and filtered. You will want to look through the keyframes and remove incorrect matches or problematic screen grabs. In my experience about 95% was correct, but a few mismatches did exist. The rest is LoRA training. Good luck.