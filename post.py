import os
import openai
from huggingface_hub import InferenceClient
from atproto import Client
from datetime import datetime, timezone
from PIL import Image, ImageOps
import requests
import io

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key)

# Initialize Bluesky client
bsky_username = os.getenv("BSKY_USERNAME")
bsky_password = os.getenv("BSKY_PASSWORD")
bsky_client = Client(base_url='https://bsky.social/xrpc')
bsky_client.login(bsky_username, bsky_password)

# Initialize Huggingface client
huggingface_key = os.getenv("HUGGINGFACE_KEY")
hf_client = InferenceClient(token=huggingface_key)

# Directory paths
txt_dir = "/path/to/project/txt/"
images_dir = "/path/to/project/images/"

# Function to generate image description
def generate_image_description():
    prompt = (
        "This is where your text prompt belongs."
         )
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an advanced AI that generates image descriptions. Your descriptions will be used by another AI to create an image based on your prompt."},
                  {"role": "user", "content": prompt}]
    )
    description = response.choices[0].message.content.strip()
    # Ensure the description is within the 300 graphemes limit
    if len(description) > 300:
        truncated_description = description[:300]
        if '.' in truncated_description:
            truncated_description = truncated_description.rsplit('.', 1)[0] + '.'
        else:
            truncated_description = truncated_description.rsplit(' ', 1)[0] + '.'
        description = truncated_description
    return description

# Function to generate image
def generate_image(description):
    headers = {"Authorization": f"Bearer {huggingface_key}"}
    payload = {"inputs": description, "options": {"wait_for_model": True}}
    response = requests.post(
        "https://api-inference.huggingface.co/models/Corcelio/mobius",
        headers=headers,
        json=payload,
        timeout=120  # Increased timeout to 120 seconds
    )
    response.raise_for_status()
    image_data = response.content
    image_pil = Image.open(io.BytesIO(image_data))
    return image_pil

# Function to save content to a file
def save_to_file(content, directory, extension):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}.{extension}"
    filepath = os.path.join(directory, filename)
    if extension == 'txt':
        with open(filepath, 'w') as file:
            file.write(content)
    else:
        content.save(filepath, format="PNG")
    return filepath

# Function to compress and save image
def compress_image(image, max_size_kb):
    buffer = io.BytesIO()
    quality = 90  # Start with high quality
    while quality > 10:  # Reduce quality until size is under limit or quality is too low
        buffer.seek(0)
        image.save(buffer, format="PNG", quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb:
            break
        quality -= 10
    buffer.seek(0)
    return buffer.read()

# Function to resize image if too large
def resize_image(image, max_size_kb):
    max_size = (1024, 1024)
    image = ImageOps.fit(image, max_size, Image.LANCZOS)
    resized_image_content = compress_image(image, max_size_kb)
    if len(resized_image_content) > max_size_kb * 1024:
        # Further reduce the resolution
        smaller_size = (512, 512)
        image = ImageOps.fit(image, smaller_size, Image.LANCZOS)
        resized_image_content = compress_image(image, max_size_kb)
    return resized_image_content

# Function to post to Bluesky
def post_to_bluesky(text_filepath, image_filepath):
    with open(text_filepath, 'r') as file:
        text_content = file.read()
    with open(image_filepath, 'rb') as file:
        image_content = file.read()

    post = {
        "$type": "app.bsky.feed.post",
        "text": text_content,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

    # Resize and compress image if it exceeds the size limit
    image = Image.open(io.BytesIO(image_content))
    resized_image_content = resize_image(image, max_size_kb=976)

    # Ensure resized image is within the size limit
    if len(resized_image_content) > 976 * 1024:
        raise ValueError("Resized image is still too large")

    # Upload image as a blob
    headers = {
        "Content-Type": "image/png",
        "Authorization": f"Bearer {bsky_client._session.access_jwt}",
    }
    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
        headers=headers,
        data=resized_image_content,
        timeout=120  # Increased timeout to 120 seconds
    )
    response.raise_for_status()
    blob = response.json()["blob"]

    post["embed"] = {
        "$type": "app.bsky.embed.images",
        "images": [{
            "alt": "Image Description", # Be sure to replace "Image Description".
            "image": blob,
        }],
    }

    # Log the post data for debugging
    print("Post data:", post)

    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {bsky_client._session.access_jwt}"},
        json={
            "repo": bsky_client._session.did,
            "collection": "app.bsky.feed.post",
            "record": post,
        },
        timeout=120  # Increased timeout to 120 seconds
    )
    # Log the response for debugging
    print("Response status code:", response.status_code)
    print("Response content:", response.content)
    
    response.raise_for_status()
    return response.json()

# Function to run the job
def job():
    try:
        description = generate_image_description()
        text_filepath = save_to_file(description, txt_dir, "txt")
        image = generate_image(description)
        image_filepath = save_to_file(image, images_dir, "png")
        post_to_bluesky(text_filepath, image_filepath)
        print("Job completed successfully.")
    except Exception as e:
        print(f"Error during job execution: {e}")

# Run the job immediately
job()
