from flask import (
    Flask,
    request,
    render_template,
    send_from_directory,
    url_for,
    jsonify,
    send_file
)

import sys, os, re, time, shutil
from gtts import gTTS
from pydub import AudioSegment
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

from logging import Formatter, FileHandler
handler = FileHandler(os.path.join(basedir, 'log.txt'), encoding='utf8')
handler.setFormatter(
    Formatter("[%(asctime)s] %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S")
)
app.logger.addHandler(handler)

UPLOAD_FOLDER = os.path.basename('./upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'srt'])


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
    print(in_file)
    current_directory = UPLOAD_FOLDER
    str_fold = os.path.basename(in_file).split('.')[0]
    str_fold = re.sub('[^a-zA-Z0-9\_\n\.\/]', '', str_fold)
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

    current_directory = os.getcwd()
    final_out_file = os.path.join(current_directory, "%s.mp3" % (str_fold))
    print(final_out_file)
    print(str_fold)
    final_song.export(final_out_file, format="mp3")
    send_file(final_out_file, attachment_filename='python.mp3')
    print('python.jpg')
    file.close()
    return final_out_file

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'js_static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     'static/js', filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    elif endpoint == 'css_static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     'static/css', filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/css/<path:filename>')
def css_static(filename):
    return send_from_directory(app.root_path + '/static/css/', filename)


@app.route('/js/<path:filename>')
def js_static(filename):
    return send_from_directory(app.root_path + '/static/js/', filename)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download/<path:filename>', methods=['POST', 'GET'])
def downloadFile (filename):
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

@app.route('/uploadajax', methods=['POST'])
def upldfile():
    if request.method == 'POST':
        files = request.files['file']
        if files and allowed_file(files.filename):
            filename = files.filename
            app.logger.info('FileName: ' + filename)
            # updir = os.path.join(basedir, 'upload/')
            updir = UPLOAD_FOLDER
            saved_file = os.path.join(updir, filename)
            files.save(saved_file)
            print("saved file path %s"%(saved_file))
            final_out_file = convert_srt_to_audio(saved_file)
            print("download is done")
            file_size = os.path.getsize(saved_file)
            return jsonify(name=filename, size=file_size, downloadpath=final_out_file)


if __name__ == '__main__':
    app.run(debug=True)
