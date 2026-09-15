import ollama

def ask_ollama(prompt):
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":
    print(ask_ollama("Explain what RAG is in one sentence."))
