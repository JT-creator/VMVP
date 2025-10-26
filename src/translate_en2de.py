from transformers import MarianMTModel, MarianTokenizer

text_list = ["The quick brown fox jumps over the lazy dog.",
             "Hello, how are you today?",]

tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de")
model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-de")

def translate(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

for text in text_list:
    translated_text = translate(text)
    print(f"EN: {text}")
    print(f"DE: {translated_text}\n")