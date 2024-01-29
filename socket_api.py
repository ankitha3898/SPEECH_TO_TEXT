import os
import io   
import sys
import wave
import json
from translate import Translator

from vosk import Model,KaldiRecognizer
import pyaudio
from flask import Flask,jsonify,request,Response
import json
import queue

from translate import Translator
from gtts import gTTS
from io import BytesIO
import pygame
import time
from flask_socketio import SocketIO

from textblob import TextBlob
# from waitress import serve
import pyaudio
from flask import Flask, render_template
from flask_socketio import SocketIO
from vosk import Model, KaldiRecognizer

app = Flask(__name__)
socketio = SocketIO(app)

# Load the Vosk model and create a recognizer
model = Model("./Vosk/vosk-model-small-en-in-0.4")

# Global variable to hold the audio stream
audio_stream = None
def wait():
    while pygame.mixer.get_busy():
        time.sleep(0)
# Define a function to process audio from the microphone and emit results
def process_microphone_audio(language):
    global audio_stream
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=19000,
                    input=True,
                    frames_per_buffer=800)
    
    while True:
        data = stream.read(4000)
        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            res = json.loads(result)
            print(res)
            print()
            translator = Translator(to_lang=language)
            translation = translator.translate(res['text'])
            pygame.init()
            pygame.mixer.init()
            mp3_fo = BytesIO()
#             x = ",".join(text1)
            tts = gTTS(translation,lang=language)

            tts.write_to_fp(mp3_fo)
            mp3_fo.seek(0)
            sound = pygame.mixer.Sound(mp3_fo)
            sound.play()
            wait()  
            socketio.emit('update_result', {'result': translation})

    result = recognizer.FinalResult()
    socketio.emit('update_result', {'result': translation})

    stream.stop_stream()
    stream.close()
    p.terminate()

# Define a WebSocket route for streaming from the microphone
@socketio.on('start_microphone_streaming')
def handle_start_microphone_streaming(data):
    global audio_stream
    # Start a background task to process audio from the microphone and emit results
    language = data.get('language', 'en')  # Default to English if not specified

    socketio.start_background_task(process_microphone_audio,language)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app,allow_unsafe_werkzeug=True )
