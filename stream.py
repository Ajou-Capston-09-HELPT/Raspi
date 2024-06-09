from flask import Flask, render_template, Response, send_file
import time
import threading
import numpy

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
@app.route('/top_accuracy_image')
def top_accuracy_image():
    image_path = '/home/pi/HELPT/topaccuracy.jpg'
    return send_file(image_path, mimetype='image/jpeg')

def main():
    app.run(host='0.0.0.0', debug=False, threaded=True)

if __name__ == "__main__":
    main()
