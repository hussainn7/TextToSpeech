from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os
import json

# Add project root to path so we can import from manage.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import functions from manage.py
from manage import bilingual_ocr, enhance_image, play_audio, is_cyrillic

# Import necessary libraries
import easyocr
import cv2
import numpy as np
import pyttsx3
import tempfile
import base64
import io
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import os
import re
from PIL import Image, ImageEnhance
from langdetect import detect, LangDetectException

# Initialize Flask app
app = Flask(__name__)

# Initialize OCR
reader_ru = easyocr.Reader(['ru'])
reader_en = easyocr.Reader(['en'])

# Initialize TTS for English
engine_en = pyttsx3.init()
engine_en.setProperty('rate', 75)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.get_json()
    img_data = data['image'].split(',')[1]  
    img_bytes = base64.b64decode(img_data)
    
    image = Image.open(io.BytesIO(img_bytes))
    
    result = bilingual_ocr(image)
    
    return jsonify(result)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)
def handler(event, context):
    with app.test_client() as client:
        path = event['path']
        
        # Handle the root path
        if path == '/.netlify/functions/app' or path == '/':
            response = client.get('/')
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'text/html',
                },
                'body': response.data.decode('utf-8')
            }
        
        # Handle API endpoints
        if path == '/.netlify/functions/app/process_image':
            # Parse the event body as JSON
            try:
                body = json.loads(event['body'])
                response = client.post('/process_image', json=body)
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'body': response.data.decode('utf-8')
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': str(e)
                }
        
        # Handle 404
        return {
            'statusCode': 404,
            'body': 'Not Found'
        } 