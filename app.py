import streamlit as st
import google.generativeai as genai
import chromadb
import warnings
import os
from dotenv import load_dotenv

# Load variables from your hidden .env file
load_dotenv()
warnings.filterwarnings("ignore")

# --- 1. UI CONFIG ---
st.set_page_config(page_title="Vedic AI Astrologer", layout="wide")
st.title("Vedic AI Astrologer 🌙")

# --- 2. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. SIDEBAR: BIRTH DATA & SETTINGS ---
with st.sidebar:
    st.header("Birth Chart Data")
    st.info("Input your manual chart details for the AI to interpret.")
    
    user_lagna = st.selectbox("Lagna (Ascendant)", [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ])
    
    user_placements = st.text_area(
        "Planetary Placements", 
        placeholder="e.g., Sun in 10th House, Moon in Taurus 4th House..."
    )
    
    st.divider()
    
    # Securely pulls your key from the .env file instead of hardcoding it!
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", type="password", value=default_key)
    
    uploaded_logic = st.file_uploader("Upload Astrology Logic (TXT)", type="txt")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CORE AI SETUP ---
model = None
collection = None

if api_key:
    genai.configure(api_key=api_key)
    
    instruction = (
        "You are a professional Vedic Astrologer. You will be provided with a birth chart. "
        "Interpret it using ONLY the context provided. Do not apologize for missing math features. "
        "Stay in character as an insightful guide."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=instruction
    )
    
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="astrology_logic")

    if uploaded_logic:
        content = uploaded_logic.read().decode("utf-8")
        collection.add(documents=[content], ids=["user_upload"])
    else:
        try:
            with open("knowledge_base.txt", "r") as f:
                content = f.read()
            collection.add(documents=[content], ids=["default_rules"])
        except FileNotFoundError:
            st.warning("Knowledge base not found. Please upload a logic file.")

# --- 5. CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your chart..."):
    if not api_key:
        st.error("Please provide an API Key in the sidebar or .env file.")
    elif collection is None:
        st.error("Database not initialized. Please provide astrology logic.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        results = collection.query(query_texts=[prompt], n_results=1)
        context = results['documents'][0][0] if results['documents'] else "No specific rules found."

        full_prompt = f"""
        USER CHART DATA:
        Lagna: {user_lagna}
        Placements: {user_placements}

        ASTROLOGICAL RULES:
        {context}

        QUESTION:
        {prompt}
        """

        response = model.generate_content(full_prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
