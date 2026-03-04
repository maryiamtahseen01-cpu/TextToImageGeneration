# image_generator.py
import requests
import base64
import os
import webbrowser
from dotenv import load_dotenv

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Config from environment
AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_URL = os.getenv("AI_API_URL")
AI_API_MODEL = os.getenv("AI_API_MODEL", "default-model")  # optional

# Do not print API keys in logs. Keep minimal debug info.
print("DEBUG: image_generator initialized")


def generate_image(prompt, style="realistic", output_file="generated.png"):
    if not AI_API_KEY:
        raise Exception("AI_API_KEY is missing in .env file")

    headers = {
        "x-api-key": AI_API_KEY
    }

    payload = {
        "prompt": f"{prompt}, {style} style",
    }

    response = requests.post(
        AI_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

    # If the API returned raw image bytes (content-type image/*), save directly
    content_type = response.headers.get('Content-Type', '') or response.headers.get('content-type', '')
    if content_type.startswith('image'):
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file

    # Otherwise expect JSON with base64-encoded image
    try:
        data = response.json()
    except Exception:
        # Avoid dumping binary to the console; show a short message instead
        raise Exception("Failed to parse JSON from API response (non-image content).")

    if "data" not in data or "image" not in data["data"]:
        raise Exception(f"Invalid API response: {data}")

    image_base64 = data["data"]["image"]
    image_bytes = base64.b64decode(image_base64)

    with open(output_file, "wb") as f:
        f.write(image_bytes)

    return output_file


# ---------------- TEST RUN ----------------
if __name__ == "__main__":
    try:
        img_path1 = generate_image(
            "A professional car spare parts banner with dark background",
            style="realistic",
            output_file="car_banner.png"
        )
        print("Image saved to:", img_path1)

        # After saving image
        webbrowser.open('file://' + os.path.realpath(img_path1))

        img_path2 = generate_image(
            "A cat in water",
            style="realistic",
            output_file="cat.png"
        )
        print("Image saved to:", img_path2)

        # After saving image
        webbrowser.open('file://' + os.path.realpath(img_path2))

        img_path3 = generate_image(
            "A mother with her son",
            style="realistic",
            output_file="Mother.png"
        )
        print("Image saved to:", img_path3)

        # After saving image
        webbrowser.open('file://' + os.path.realpath(img_path3))

    except Exception as e:
        print("ERROR:", e)
