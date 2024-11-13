# This file goes through all of the images in our dataset and uses GPT-4o to 
# determine the text that is in the image. It stores each text file in 
# [datasetname]/ProcessedText/[imageFileName].txt
from openai import OpenAI
import base64
from PIL import Image
import os
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL="gpt-4o"
IMAGE_DIRECTORY_NAME = "BLN600Dataset/Images/"
PROCESSED_TEXT_DIRECTORY_NAME = "BLN600Dataset/ProcessedText/"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

num_images_processed = 0
start = time.time()

print(f"Starting processing at {start} time")

for image_filename in os.listdir(IMAGE_DIRECTORY_NAME):
    # If that image has already been processed, skip its processing
    if os.path.exists(PROCESSED_TEXT_DIRECTORY_NAME + image_filename[:-4] + ".txt") \
        and os.path.isfile(PROCESSED_TEXT_DIRECTORY_NAME + image_filename[:-4] + ".txt"):
        print(f"Text already processed for {image_filename}... skipping")
        continue

    image_path = IMAGE_DIRECTORY_NAME + image_filename
    
    # Convert TIFF files to JPEG if necessary
    if image_filename.lower().endswith(".tif"):
        tiff_image = Image.open(image_path)
        jpeg_image_path = image_path[:-4] + ".jpg"
        jpeg_image = tiff_image.convert("RGB")
        jpeg_image.save(jpeg_image_path)
        image_path = jpeg_image_path
    
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that can look at an image and accurately tell me all of the text on. Help me determine the text on the following images."},
            {"role": "user", "content": [
                {"type": "text", "text": "What is all of the text on this newspaper clip? I just need the raw text, nothing else."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )

    OUTPUT_FILE = PROCESSED_TEXT_DIRECTORY_NAME + image_filename[:-4] + ".txt"
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(response.choices[0].message.content + "\n\n")
    
    print(f"Just processed image {image_path}")
    num_images_processed += 1

end = time.time()
print(f"Finshed processing at {end} time")
print(f"Took {end - start} seconds to process {num_images_processed} images.")
print(f"AVERAGE TIME: {(end - start) / num_images_processed} sec/image")