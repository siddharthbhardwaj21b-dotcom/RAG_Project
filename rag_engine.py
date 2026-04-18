import google.generativeai as genai
import chromadb
import warnings
import os
from dotenv import load_dotenv

# Keep the terminal clean and load secrets from your Mac
warnings.filterwarnings("ignore")
load_dotenv()

# 1. SETUP THE AI
API_KEY = os.getenv("GEMINI_API_KEY")

# Safety check so it doesn't crash if the .env file is missing
if not API_KEY:
    print("Error: No API key found. Please check your .env file.")
    exit()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. LOAD YOUR DOCUMENT
print("1. Reading the Knowledge Base...")
try:
    with open("knowledge_base.txt", "r") as file:
        document_text = file.read()
except FileNotFoundError:
    print("Error: knowledge_base.txt not found. Please create it.")
    exit()

# 3. SETUP THE VECTOR DATABASE
print("2. Storing document in ChromaDB...")
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="astrology_docs")

# Add your text file into the database
collection.add(
    documents=[document_text],
    metadatas=[{"source": "astrology_rules"}],
    ids=["doc1"]
)

# 4. THE CHAT LOOP
print("\n--- AI Assistant is Ready! (Type 'exit' to quit) ---")

while True:
    # Get user input from the terminal
    user_question = input("\nYou: ")
    
    # Check if the user wants to quit
    if user_question.lower() == 'exit':
        print("Goodbye!")
        break

    # Search the database for the answer
    results = collection.query(
        query_texts=[user_question],
        n_results=1
    )
    
    # Handle empty database scenarios gracefully
    retrieved_context = results['documents'][0][0] if results['documents'] else "No context found."

    # Generate the answer
    strict_prompt = f"""
    You are a professional Vedic Astrologer. Answer the question using ONLY the context provided below. 
    
    Context:
    {retrieved_context}

    Question:
    {user_question}
    """
    
    response = model.generate_content(strict_prompt)
    print(f"AI: {response.text}")
