# Video to Text Converter

A simple web application that converts video files to text using Streamlit, MoviePy, and Google's Speech Recognition.

## Features

- Upload video files (supports MP4, AVI, MOV, MKV formats)
- Convert videos to text using speech recognition
- Display transcribed text
- Download transcribed text as a text file
- Simple and user-friendly interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) If you want to use Google Gemini API features, create a `.env` file in the project root and add your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the Application

To run the application, use the following command:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

1. Click on the "Choose a video file" button to upload a video
2. Once uploaded, you'll see the file details
3. Click the "Convert to Text" button to start the conversion
4. After conversion, you can:
   - View the transcribed text directly in the browser 
   - Download the transcribed text as a text file

## Requirements

- Python 3.7 or higher
- Streamlit
- MoviePy
- SpeechRecognition
- pydub
- google-generativeai (optional)
- python-dotenv (optional)

## Note

This application uses Google's Speech Recognition API for transcription. Make sure you have a stable internet connection for the transcription to work properly. 

