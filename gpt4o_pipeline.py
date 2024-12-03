from openai import OpenAI
import base64
import os
import time
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
MAX_RETRIES = 5
BACKOFF_FACTOR = 2  # Exponential backoff factor


import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config='--psm 1 --oem 1')
    print(text)
    return text

extract_text_from_image("/Users/rachelclinton/Desktop/224v-openai-processing/evaluation_data/moderate_layout/loc_anchoragedaily_31oct1916.png")

'''
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_text_with_retry(base64_image, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            # image_data = base64.b64decode(base64_image)
            # debug_image = Image.open(BytesIO(image_data))

            # plt.imshow(debug_image)
            # plt.title(f"Segment Attempt {attempt + 1}")
            # plt.show()
            print("trying to use chatgpt here")
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts text from images accurately.",
                    },
                    {
                        "role": "user",
                        "content": f"Here is an image in base64 format: data:image/png;base64,{base64_image}. Please extract all visible text.",
                    },
                ],
                temperature=0.0,
            )
            print("HERE2")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return "Rate limit error: Could not process the image."


def extract_text_from_image(image_path, segments=4, direction="vertical"):
    image = Image.open(image_path)
    image = image.resize(
        (int(image.width / 5), int(image.height / 5)),
        Image.LANCZOS 
    )

    width, height = image.size

    full_text = ""

    # Segment the image and process each part
    for i in range(segments):
        if direction == "vertical":
            # Calculate vertical segment boundaries
            top = i * (height // segments)
            bottom = (i + 1) * (height // segments) if i < segments - 1 else height
            cropped_image = image.crop((0, top, width, bottom))
        else:
            # Calculate horizontal segment boundaries
            left = i * (width // segments)
            right = (i + 1) * (width // segments) if i < segments - 1 else width
            cropped_image = image.crop((left, 0, right, height))

        # Convert cropped segment to base64
        buffer = BytesIO()
        cropped_image.save(buffer, format="PNG")
        # base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_image = encode_image(image_path)
    
        # Process the segment with OpenAI
        segment_text = extract_text_with_retry(base64_image)
        full_text += segment_text + "\n"  # Append segment text to full text
        print(full_text)

    return full_text

# Input and output base directories
input_base_dir = "evaluation_data"
output_base_dir = "gpt4o_pipeline_output"

num_images_processed = 0
start_time = time.time()

for category in os.listdir(input_base_dir):
    if category != "handwritten":  # Skip categories that aren't "handwritten"
        continue

    category_path = os.path.join(input_base_dir, category)
    if os.path.isdir(category_path):
        for image_folder in os.listdir(category_path):
            image_path = os.path.join(category_path, image_folder)
            # im  = Image.open(image_path)
            # plt.imshow(im)
            # plt.axis("off")  # Turn off axes for better visualization
            # plt.title(f"Processing: {image_folder}")
            # plt.show()
            print(f"Processing: {image_path}")

            extracted_text = extract_text_from_image(image_path, segments=4, direction="vertical")

            output_category_dir = os.path.join(output_base_dir, category)
            output_folder_dir = os.path.join(output_category_dir, image_folder)
            os.makedirs(output_folder_dir, exist_ok=True)

            output_file_path = os.path.join(output_folder_dir, f"{image_path}.txt")
            with open(output_file_path, "w") as output_file:
                output_file.write(extracted_text)

            print(f"Text extracted and saved for {image_path}")
            num_images_processed += 1

# end_time = time.time()
# print(f"Processed {num_images_processed} images in {end_time - start_time} seconds.")
# print(f"Average time per image: {(end_time - start_time) / num_images_processed:.2f} seconds.")'''