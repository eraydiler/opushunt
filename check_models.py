import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API Key not found in .env")
        return

    print(f"Using API Key: {api_key[:5]}...{api_key[-3:]}")

    try:
        client = genai.Client(api_key=api_key)
        print("Client created. Attempting to list models...")

        # In the new SDK, listing models might differ, but let's try the standard way
        # Note: The new SDK structure is client.models.list()
        response = client.models.list()

        print("\n--- Available Models ---")
        found_any = False
        for model in response:
            # The model object attributes might vary, let's try to print name/display_name
            # It usually returns an object with .name
            print(f"- {model.name}")
            found_any = True

        if not found_any:
            print("No models found in the list.")

    except Exception as e:
        print(f"\nERROR Listing Models: {e}")
        # Try to print more details if it's an API error
        if hasattr(e, 'message'):
            print(f"Message: {e.message}")
        if hasattr(e, 'code'):
            print(f"Code: {e.code}")


if __name__ == "__main__":
    list_available_models()
