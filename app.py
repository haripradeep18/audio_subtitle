import os,cv2
from flask import Flask, render_template, request,jsonify, send_file
from PIL import Image

import numpy as np
import time

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('.')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

start_time = time.time()


def convert_milliseconds(t):
    hours, minutes, seconds = (t.split(":"))
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)
    miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
    return miliseconds


def convert_srt_to_audio(in_file):
    file = open(in_file, "r", encoding='utf-8')
    lines = file.read()

    current_directory = UPLOAD_FOLDER
    str_fold = in_file.split('.')[0]
    str_directory = os.path.join(current_directory, str_fold)
    if not os.path.exists(str_directory):
        os.makedirs(str_directory)

    all_dialogs = lines.strip().split("\n\n")
    final_song = None
    privious_time = 0

    for dialog in all_dialogs[:2]:
        each_dialog = dialog.split("\n")
        count, times, dia_text = "%s" % (each_dialog[0]), each_dialog[1], " ".join(each_dialog[2:])
        start_time_str, end_time_str = times.split('-->')
        start_time = convert_milliseconds(start_time_str.split(',')[0].strip())
        end_time = convert_milliseconds(end_time_str.split(',')[0].strip())

        speech = gTTS(text=dia_text, lang='ta', slow=False)
        each_dialog_file = os.path.join(str_directory, "%s.mp3" % (count))
        out_file = re.sub('[^a-zA-Z0-9\_\n\.\/]', '', each_dialog_file)
        print(out_file)
        speech.save(out_file)
        silent_milli_seconds = start_time - privious_time
        # create 1 sec of silence audio segment
        silent_segment = AudioSegment.silent(duration=silent_milli_seconds)  # duration in milliseconds

        # read wav file to an audio segment
        dia_file = AudioSegment.from_mp3(out_file)

        # Add above two audio segments
        if out_file.split('/')[-1] == "1.mp3":
            final_song = silent_segment + dia_file
        else:
            final_song = final_song + silent_segment + dia_file
        privious_time = end_time

    final_out_file = "%s.mp3" % (in_file.split('.')[0])
    os.remove(str_directory)
    final_song.export(final_out_file, format="mp3")
    return send_file(final_out_file, as_attachment=True)
    file.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ocr', methods=['POST','GET'])
def upload_file():
    if request.method == "GET":
        return "This is the api BLah blah"
    elif request.method == "POST":
        file = request.files['image']

        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)
        file.save(f)
        # print(file.filename)

        file_name = UPLOAD_FOLDER+"/"+file.filename
        final_output = convert_srt_to_audio(file_name)

        # final_output = read_text_from_image(file_name, small_text, vertical_text)
        # if os.path.exists(UPLOAD_FOLDER + '/sub_images'): os.remove(UPLOAD_FOLDER + '/sub_images')
        os.remove(UPLOAD_FOLDER + "/" + file.filename)

        return jsonify({"text" : text})

app.run("0.0.0.0",5000,threaded=True,debug=True)


