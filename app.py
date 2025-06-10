import streamlit as st
import os
from moviepy.editor import VideoFileClip
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
import wave
import contextlib
import time

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_audio_duration(audio_path):
    with contextlib.closing(wave.open(audio_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

def convert_video_to_audio(video_file):
    # Create a temporary file to store the video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(video_file.read())
        temp_video_path = temp_video.name

    # Create a temporary file for the audio
    temp_audio_path = temp_video_path.replace('.mp4', '.wav')

    try:
        # Load the video file
        video = VideoFileClip(temp_video_path)
        
        # Extract the audio
        audio = video.audio
        
        # Write the audio to a file with specific parameters
        audio.write_audiofile(
            temp_audio_path,
            fps=16000,  # Sample rate
            nbytes=2    # Sample width
        )
        
        # Close the video and audio files
        video.close()
        audio.close()
        
        # Give some time for the file to be fully written
        time.sleep(1)
        
        return temp_audio_path
    except Exception as e:
        st.error(f"Error converting video to audio: {str(e)}")
        return None
    finally:
        # Clean up the temporary video file
        try:
            if os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
        except Exception as e:
            st.warning(f"Could not delete temporary video file: {str(e)}")

def transcribe_audio(audio_path):
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Get audio duration
        duration = get_audio_duration(audio_path)
        
        # If audio is longer than 1 minute, we'll need to process it in chunks
        if duration > 60:
            st.warning("Audio is longer than 1 minute. Processing in chunks...")
            return transcribe_long_audio(audio_path)
        
        # Load audio file
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            
            # Record the audio data
            audio_data = recognizer.record(source)
            
            # Use Google's speech recognition
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        st.error("Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Speech Recognition service; {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def transcribe_long_audio(audio_path):
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file
        audio = AudioSegment.from_wav(audio_path)
        
        # Split audio into 30-second chunks
        chunk_length_ms = 30000
        chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        
        full_text = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Export chunk to temporary file
            chunk_path = f"{audio_path}_chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            
            # Transcribe chunk
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    full_text.append(text)
                except sr.UnknownValueError:
                    st.warning(f"Could not understand audio in chunk {i+1}")
                except sr.RequestError as e:
                    st.error(f"Error in chunk {i+1}: {str(e)}")
            
            # Clean up chunk file
            try:
                if os.path.exists(chunk_path):
                    os.unlink(chunk_path)
            except Exception as e:
                st.warning(f"Could not delete temporary chunk file: {str(e)}")
            
            # Update progress
            st.progress((i + 1) / len(chunks))
        
        return " ".join(full_text)
    except Exception as e:
        st.error(f"Error processing long audio: {str(e)}")
        return None

def main():
    st.title("Video to Text Converter")
    st.write("Upload a video file to convert it to text")

    # File uploader
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov', 'mkv'])

    if uploaded_file is not None:
        # Display video information
        file_details = {
            "Filename": uploaded_file.name,
            "FileSize": f"{uploaded_file.size / 1024 / 1024:.2f} MB"
        }
        st.write("File Details:", file_details)

        # Convert button
        if st.button("Convert to Text"):
            with st.spinner("Converting video to text..."):
                # First convert video to audio
                audio_path = convert_video_to_audio(uploaded_file)
                
                if audio_path:
                    # Then transcribe the audio to text
                    text = transcribe_audio(audio_path)
                    
                    if text:
                        # Display the transcribed text
                        st.subheader("Transcribed Text:")
                        st.write(text)
                        
                        # Add a download button for the text
                        st.download_button(
                            label="Download Text File",
                            data=text,
                            file_name=f"{os.path.splitext(uploaded_file.name)[0]}.txt",
                            mime="text/plain"
                        )
                    
                    # Clean up the temporary audio file
                    try:
                        if os.path.exists(audio_path):
                            os.unlink(audio_path)
                    except Exception as e:
                        st.warning(f"Could not delete temporary audio file: {str(e)}")

if __name__ == "__main__":
    main() 