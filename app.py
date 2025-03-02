from flask import Flask, request, jsonify
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io
import base64

app = Flask(__name__)

# Load the Stable Diffusion model
try:
    model_id = "stabilityai/stable-diffusion-2-1"  # Updated model for 2025 compatibility
    print(f"Loading model: {model_id}")
    
    # Ensure float32 precision for CPU compatibility
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
    print(f"Model loaded successfully on {device}.")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

@app.route('/generate', methods=['POST'])
def generate_image():
    # Get the text prompt from the request
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Generate the image using the model
    print(f"Generating image for: '{prompt}'")
    try:
        with torch.no_grad():  # Disable gradient computation for inference
            image = pipe(prompt).images[0]

        # Convert the image to base64 for sending to the frontend
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({"image": img_str})
    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({"error": "An error occurred while generating the image."}), 500

if __name__ == '__main__':
    app.run(debug=True)
