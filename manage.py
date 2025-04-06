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
from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageEnhance
from langdetect import detect, LangDetectException

app = Flask(__name__)

# Инициализация OCR
reader_ru = easyocr.Reader(['ru'])
reader_en = easyocr.Reader(['en'])

# Инициализация TTS для английского
engine_en = pyttsx3.init()
engine_en.setProperty('rate', 75)  # чем ниже тем медленнее

def is_cyrillic(text):
    """Check if text is predominantly Cyrillic"""
    cyrillic_chars = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
    return cyrillic_chars / max(1, len(text)) > 0.6

def play_audio(text, language):
    """Play audio in the specified language"""
    try:
        if language == 'ru':
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tts = gTTS(text=text, lang='ru', slow=False)
                tts.save(tmp.name)
                
                data, fs = sf.read(tmp.name)
                sd.play(data, fs)
                sd.wait()  
                
                os.unlink(tmp.name)
        else:
            # pyttsx3 для English
            engine_en.say(text)
            engine_en.runAndWait()
            
    except Exception as e:
        print(f"Error in TTS playback: {e}")

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
        print("Detected Russian text:", ru_text)
        play_audio(ru_text, 'ru')
        return {"text": ru_text, "language": "ru"}
    else:
        print("Detected English text:", en_text)
        play_audio(en_text, 'en')
        return {"text": en_text, "language": "en"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.get_json()
    img_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64 prefix
    img_bytes = base64.b64decode(img_data)
    
    image = Image.open(io.BytesIO(img_bytes))
    
    result = bilingual_ocr(image)
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
