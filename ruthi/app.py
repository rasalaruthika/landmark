import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import speech_recognition as sr
import folium
from streamlit_folium import folium_static
import requests
import pyttsx3
import base64
import geocoder

# Set Google Gemini API Key
API_KEY = "your_gemini_api_key_here"
genai.configure(api_key=API_KEY)

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1)

def text_to_speech(text, filename="output.mp3"):
    """Convert text to speech and save as an audio file."""
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

def get_place_description(place_name):
    """Generate AI description of the given place."""
    try:
        prompt = f"Provide a detailed travel guide for {place_name}, including history, best things to do, local cuisine, and travel tips."
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else "No details available."
    except Exception as e:
        return f"Error fetching place description: {e}"

# Streamlit App Title
st.title("🌍 AI Tour Guide - Travel Companion")
st.markdown("Explore landmarks, plan trips & estimate travel costs! 🚀")

# Automatically Get User's Location
st.subheader("📍 Detecting Your Location...")
location = geocoder.ip("me")

if location.ok:
    latitude, longitude = location.latlng
    st.success(f"Your Location: Latitude = {latitude}, Longitude = {longitude}")
else:
    st.warning("Could not determine your location. Please enter manually.")

# Interactive Map
if location.ok:
    map_obj = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Marker([latitude, longitude], popup="Your Location").add_to(map_obj)
    folium_static(map_obj)

# 🎙 Voice Input
st.sidebar.title("🎙 Speak a Place Name")
recognizer = sr.Recognizer()
spoken_place = ""

if st.sidebar.button("Record Place Name"):
    with sr.Microphone() as source:
        st.sidebar.write("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            spoken_place = recognizer.recognize_google(audio)
            st.sidebar.success(f"Recognized Place: {spoken_place}")
        except sr.UnknownValueError:
            st.sidebar.error("Could not understand audio.")
        except sr.RequestError:
            st.sidebar.error("Speech Recognition service unavailable.")

# 📸 Upload or Capture Image
st.subheader("📸 Upload or Capture an Image")
uploaded_image = st.file_uploader("Upload an image", type=['jpg', 'png', 'jpeg'])
camera_image = st.camera_input("Take a picture")

# Text Input
st.subheader("📍 Enter a Place Name")
manual_place = st.text_input("Enter a place name")

# Determine Input
final_place = spoken_place if spoken_place else manual_place

# Process Image for Landmark Recognition
if uploaded_image or camera_image:
    st.image(uploaded_image or camera_image, caption="Uploaded Landmark", use_column_width=True)
    try:
        image = Image.open(uploaded_image) if uploaded_image else Image.open(camera_image)
        prompt = "Describe this landmark in detail, including history and travel tips."
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([image, prompt])

        if hasattr(response, 'text'):
            final_place = response.text.split("\n")[0]  
            st.subheader("📜 AI-Generated Landmark Description:")
            st.write(response.text)

            # Text-to-Speech Conversion
            audio_file = text_to_speech(response.text)
            with open(audio_file, "rb") as audio:
                audio_bytes = audio.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                    <audio controls>
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.error("Could not recognize the image.")
    except Exception as e:
        st.error(f"Error processing image: {e}")

# Generate Description for Text/Voice Input
if final_place:
    st.subheader(f"🗺 AI Tour Guide for {final_place}")
    description = get_place_description(final_place)
    st.write(description)

    # Convert Description to Speech
    audio_file = text_to_speech(description)
    with open(audio_file, "rb") as audio:
        audio_bytes = audio.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio controls>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown("Built by GeoIntellects 💡")