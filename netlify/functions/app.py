from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os
import json

# Add project root to path so we can import from manage.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Find the template directory
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')

# Import functions from manage.py
from manage import bilingual_ocr, enhance_image, play_audio, is_cyrillic

# Import necessary libraries
import easyocr
import cv2
import numpy as np
import base64
import io
from PIL import Image, ImageEnhance
from langdetect import detect, LangDetectException

# Initialize Flask app
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize OCR
reader_ru = easyocr.Reader(['ru'])
reader_en = easyocr.Reader(['en'])

def is_cyrillic(text):
    """Check if text is predominantly Cyrillic"""
    cyrillic_chars = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
    return cyrillic_chars / max(1, len(text)) > 0.6

def enhance_image(image):
    """Enhanced image preprocessing for better OCR results"""
    if isinstance(image, np.ndarray):
        pil_image = Image.fromarray(image)
    else:
        pil_image = image
        
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_img = enhancer.enhance(1.5)
    
    enhancer = ImageEnhance.Sharpness(enhanced_img)
    enhanced_img = enhancer.enhance(1.5)
    
    enhanced_np = np.array(enhanced_img)
    
    if len(enhanced_np.shape) == 3:
        gray_image = cv2.cvtColor(enhanced_np, cv2.COLOR_RGB2GRAY)
    else:
        gray_image = enhanced_np
        
    binary_image = cv2.adaptiveThreshold(
        gray_image, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )
    
    kernel = np.ones((1, 1), np.uint8)
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
    binary_image = cv2.dilate(binary_image, kernel, iterations=1)
    
    return binary_image

def bilingual_ocr(image):
    """Process image with OCR for both Russian and English"""
    processed_image = enhance_image(image)
    
    ru_results = reader_ru.readtext(processed_image, detail=0, paragraph=True)
    ru_text = " ".join(ru_results)
    
    en_results = reader_en.readtext(processed_image, detail=0, paragraph=True)
    en_text = " ".join(en_results)
    
    if not ru_text and not en_text:
        ru_results = reader_ru.readtext(image, detail=0, paragraph=True)
        ru_text = " ".join(ru_results)
        
        en_results = reader_en.readtext(image, detail=0, paragraph=True)
        en_text = " ".join(en_results)
    
    if not ru_text.strip() and not en_text.strip():
        return {"text": "No text detected", "language": "unknown"}
        
    if is_cyrillic(ru_text):
        return {"text": ru_text, "language": "ru"}
    else:
        return {"text": en_text, "language": "en"}

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
    return send_from_directory(static_dir, path)

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
        
        # Handle static files
        if path.startswith('/.netlify/functions/app/static/'):
            file_path = path.replace('/.netlify/functions/app/static/', '')
            response = client.get(f'/static/{file_path}')
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'text/plain',
                },
                'body': response.data.decode('utf-8')
            }
        
        # Handle 404
        return {
            'statusCode': 404,
            'body': 'Not Found'
        } 