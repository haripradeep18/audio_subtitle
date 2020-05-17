# convert subtitle to audio
A simple flask app that takes an srt file as input and returns the audio(.mp3) within it.

## Install python packages
- flask
- pydub
- gTTS
- gTTS-token

## Use 
  - Run the application
    ```python app.py```
    Run the web application and use it.
  - API
    api end point
    ```curl -i -X POST -F files=@subtitle.srt http://127.0.0.1:5000/api/download```
    also add the preprocess parameter (thresh or blur).

## Screenshots

