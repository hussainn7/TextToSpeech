# Camera OCR Text-to-Speech

A web application that uses your camera to capture text, recognize it (in both Russian and English), and read it aloud.

## Features

- Real-time camera access and image capture
- Automatic language detection (Russian & English)
- Text-to-Speech output based on the detected language
- Image enhancement for better text recognition
- Modern, mobile-friendly user interface

## Requirements

- Python 3.7+
- Web browser with camera access

## Installation

1. Clone the repository:
```
git clone https://github.com/hussainn7/TextToSpeech.git
cd TextToSpeech
```

2. Create a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

## Usage

1. Start the application:
```
python manage.py
```

2. Open a web browser and navigate to:
```
http://localhost:5020
```

3. Allow camera access when prompted
4. Point your camera at text (in Russian or English)
5. Click the "Capture Text" button
6. The application will recognize the text, display it, and read it aloud

## How It Works

1. The application captures an image from your camera
2. The image is preprocessed to improve text visibility
3. EasyOCR is used to detect text in both Russian and English
4. Language detection determines the language of the text
5. Text-to-Speech engines (gTTS for Russian, pyttsx3 for English) read the detected text

## Technologies Used

- Flask: Web framework
- EasyOCR: Optical Character Recognition
- OpenCV & PIL: Image processing
- gTTS & pyttsx3: Text-to-Speech
- langdetect: Language detection 