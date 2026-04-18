# Open the file in "read" mode
with open("knowledge_base.txt", "r") as file:
    document_text = file.read()

print("I successfully read the document! Here is a preview of what it says:\n")
print(document_text[:100] + "...") # Prints just the first 100 characters