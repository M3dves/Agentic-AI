from openai import OpenAI
import sys

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def run_chat_loop():
    # Initialize conversation history with a system prompt/persona
    messages = [
        {
            "role": "system",
            "content": "You are a helpful academic mentor. Respond clearly and concisely."
        }
    ]

    print("Chat session started. Type 'quit' or 'exit' to end the conversation.\n")

    while True:
        #Read user input from stdin
        try:
            user_input = input("User: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        # Support an exit command
        if user_input.strip().lower() in ['quit', 'exit']:
            print("Ending chat session. Goodbye!")
            break

        if not user_input.strip():
            continue

        #Append user input to the message history
        messages.append({"role": "user", "content": user_input})

        try:
            # Dispatch the full history to the model
            response = client.chat.completions.create(
                model="qwen2.5:1.5b",
                temperature=0.2,
                messages=messages
            )

            assistant_reply = response.choices[0].message.content

            #Print the model's response
            print(f"Assistant: {assistant_reply}\n")

            # Append the assistant's reply back to the history
            messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print(f"Error communicating with Ollama: {e}\n")
            # Remove the last user message so it doesn't break future context if retried
            messages.pop()

if __name__ == "__main__":
    run_chat_loop()