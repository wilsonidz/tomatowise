# TomatoWise - AI Assistant for Nigerian Tomato Farmers
# Streamlit App Code with Voice Input and Text-to-Speech

import streamlit as st
import openai
import pandas as pd
import os
from gtts import gTTS
import base64
import tempfile
import speech_recognition as sr
import pydub
from pydub import AudioSegment

# ------------------ Configuration ------------------
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# ------------------ Load Market Price Data ------------------
def load_price_data():
    data = {
        "Location": ["Kaduna", "Kano", "Jos", "Lagos"],
        "Price per Basket (₦)": [14000, 15000, 16000, 17000]
    }
    return pd.DataFrame(data)

# ------------------ AI Response Generator ------------------
def get_advice_from_ai(query, language):
    base_prompt = f"You are an expert tomato farming advisor in Nigeria. A farmer says: '{query}'. Respond with helpful, practical advice."
    if language == "English":
        prompt = base_prompt + " Respond in simple English."
    elif language == "Hausa":
        prompt = base_prompt + " Respond in Hausa language."
    elif language == "Yoruba":
        prompt = base_prompt + " Respond in Yoruba language."
    else:
        prompt = base_prompt

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ Convert Text to Speech ------------------
def text_to_speech(text, language_code="en"):
    lang_map = {"English": "en", "Hausa": "ha", "Yoruba": "yo"}
    tts = gTTS(text=text, lang=lang_map.get(language_code, "en"))
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# ------------------ Speech Recognition ------------------
def transcribe_audio(uploaded_file):
    try:
        audio = AudioSegment.from_file(uploaded_file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            audio.export(temp_wav.name, format="wav")
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav.name) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Could not transcribe: {str(e)}"

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="TomatoWise AI", layout="centered")
st.title("🍅 TomatoWise - AI Assistant for Tomato Farmers")
st.write("Empowering Nigerian tomato farmers with smart advice and market insights.")

option = st.sidebar.selectbox("What would you like to do?", ["Get Farming Advice", "Diagnose a Problem", "Check Market Prices"])

if option in ["Get Farming Advice", "Diagnose a Problem"]:
    st.subheader("Ask a question about your farm")
    language = st.selectbox("Select your preferred language:", ["English", "Hausa", "Yoruba"])
    voice_input = st.file_uploader("Or upload a voice note (MP3/WAV)", type=["mp3", "wav"])
    user_input = ""

    if voice_input:
        with st.spinner("Transcribing audio..."):
            user_input = transcribe_audio(voice_input)
            st.success("Transcription complete")
            st.write(f"You said: {user_input}")
    else:
        user_input = st.text_area("Or type your issue/question:")

    if st.button("Get Advice") and user_input:
        with st.spinner("Getting advice from AI..."):
            result = get_advice_from_ai(user_input, language)
            st.success("Here's what we suggest:")
            st.write(result)
            audio_path = text_to_speech(result, language)
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")

elif option == "Check Market Prices":
    st.subheader("Tomato Market Prices (Simulated)")
    df = load_price_data()
    st.table(df)
    st.info("These prices are sample data and can be replaced with real-time data sources in the future.")

st.markdown("---")
st.markdown("Built by 3MTT Fellow Wilson Idzi | #3MTTLearningCommunity #Му3МТТ")
