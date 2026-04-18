import google.generativeai as genai
import chromadb
import warnings

# Keep the terminal clean
warnings.filterwarnings("ignore")

# 1. SETUP THE AI
API_KEY = "AIzaSyBOMACqTvxVmMXurnCSkZsVbjhv9sR4cT0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. LOAD YOUR DOCUMENT
print("1. Reading the Product Document...")
with open("knowledge_base.txt", "r") as file:
    document_text = file.read()

# 3. SETUP THE VECTOR DATABASE
print("2. Storing document in ChromaDB...")
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="product_docs")

# We add your text file into the database. Behind the scenes, 
# Chroma translates this text into numbers (embeddings) so it can be searched.
collection.add(
    documents=[document_text],
    metadatas=[{"source": "PRD_Draft"}],
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
    retrieved_context = results['documents'][0][0]

    # Generate the answer
    strict_prompt = f"""
    You are a helpful Product Assistant. Answer the question using ONLY the context provided below. 
    
    Context:
    {retrieved_context}

    Question:
    {user_question}
    """
    
    response = model.generate_content(strict_prompt)
    
    print(f"AI: {response.text}")

# Search the database for the answer
results = collection.query(
    query_texts=[question],
    n_results=1
)
retrieved_context = results['documents'][0][0]

# 5. GENERATE THE FINAL ANSWER
print("4. Sending retrieved context to Gemini...")

# We build a strict prompt forcing the AI to use ONLY the database info
strict_prompt = f"""
You are a helpful Product Assistant. Answer the question using ONLY the context provided below. 
Do not use any outside knowledge.

Context:
{retrieved_context}

Question:
{question}
"""

response = model.generate_content(strict_prompt)

print("\n--- FINAL AI RESPONSE ---")
print(response.text)