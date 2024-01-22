#!/usr/bin/env python
# coding: utf-8

# In[1]:


from vosk import Model,KaldiRecognizer
import pyaudio
from flask import Flask,jsonify,request,Response
import json
from translate import Translator
from gtts import gTTS
from io import BytesIO
import pygame
import time
from textblob import TextBlob
#from waitress import serve


# In[2]:


app=Flask(__name__)

@app.route("/")
def index():
    return "running "
from threading import Thread
model=Model("./Vosk/vosk-model-small-en-in-0.4")
recogniser=KaldiRecognizer(model,16000)
mic=pyaudio.PyAudio()
stream=mic.open(rate=19000,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=3200)
stream.start_stream()
text1=[]
def scanning():
    while True:
        data=stream.read(3200)
        if recogniser.AcceptWaveform(data):


            text=recogniser.Result()
            res = json.loads(text)
            print(res)
            print()
            translator = Translator(to_lang=lang)
            translation = translator.translate(res['text'])


            text1.append(translation)
            print(text1)

        if stop == 1:   
            break   #Break while loop when stop = 1
@app.route('/start',methods=['POST'])

def start_thread():
    # Assign global variable and initialize value
    global lang
    lang=request.form['Language']
    print(lang)

    global stop
    stop = 0

    # Create and launch a thread 
    t = Thread (target = scanning)
    t.start()
    return jsonify(text1)
@app.route('/stop')

def stop():
    # Assign global variable and set value to stop
    global stop
    stop = 1
    return 'stop'
@app.route('/save')

def save_file():
    print('this is text1',text1)
    textfile=open('text.txt','w',encoding="utf-8")
    for i in text1:
        textfile.write(i)
        textfile.write('\n')
    textfile.close()    
    return 'saved'  
def wait():
    while pygame.mixer.get_busy():
        time.sleep(.1)

@app.route('/chattrans',methods=['POST'])
def chattrans():
#     text1=['hi','jlo','can u hear me']
    language=request.form['lang']
    print(language)
    pygame.init()
    pygame.mixer.init()
    mp3_fo = BytesIO()
    x = ",".join(text1)
    tts = gTTS(x,lang=language)

    tts.write_to_fp(mp3_fo)
    mp3_fo.seek(0)
    sound = pygame.mixer.Sound(mp3_fo)
    sound.play()
    wait()   
    return 'success'
def Convert(tup, di):
    di = dict(tup)
    return di
@app.route('/feebback')
def feedback():
    x = ",".join(text1)
    txt=TextBlob(x).tags
    dictionary = {}
    dict1=Convert(txt, dictionary)
    words=[]
    for i,j in dict1.items():
        if j=='JJ':
            words.append(i) 
            print(i)
    return jsonify(words) 
converted=[]
from deep_translator import GoogleTranslator
@app.route('/sts')
def speech():
    language=request.form['lang']

    translator = GoogleTranslator(source=lang, target=language)
    pygame.init()
    pygame.mixer.init()
    mp3_fo = BytesIO()
    for x in text1:
        x=x.strip()
        
        trans=translator.translate(x)
        converted.append(trans)
    x = ",".join(converted)
    tts = gTTS(x,lang=language)

    tts.write_to_fp(mp3_fo)
    mp3_fo.seek(0)
    sound = pygame.mixer.Sound(mp3_fo)
    sound.play()
    wait()   
    return 'success'     
    


    


# In[ ]:


if __name__=='__main__':
    app.run(port=30)


# In[ ]:




