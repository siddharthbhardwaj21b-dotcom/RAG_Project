import google.generativeai as genai
import warnings

# Suppress those annoying warnings so your terminal stays clean
warnings.filterwarnings("ignore")

# 1. Provide your secret key
API_KEY = "AIzaSyBOMACqTvxVmMXurnCSkZsVbjhv9sR4cT0"
genai.configure(api_key=API_KEY)

# 2. Pick the brain from your specific menu
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Ask a question and print the answer
print("Asking the AI...")
response = model.generate_content("You are an AI assistant. In one sentence, tell me you are ready to build a RAG system.")

print("\nAI Response:")
print(response.text)