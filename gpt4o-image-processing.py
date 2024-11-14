# This file goes through all of the images in our dataset and uses GPT-4o to 
# determine the text that is in the image. It stores each text file in 
# [newspaperName]/gpt4o_processed_text/[newspaperNumber/[imageFileName].txt
from openai import OpenAI
import base64
import os
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL="gpt-4o"
NEWSPAPER_DIRECTORY_NAMES = ["1798_newspapers/", "1827_newspapers/"]
FULL_NEWSPAPER_IMAGES_DIRECTORY_NAME = "full_newspaper_images/"
GPT4O_PROCESSED_TEXT_DIRECTORY_NAME = "gpt4o_processed_text/"
SEGMENTED_NEWSPAPER_IMAGES_DIRECTORY_NAMES = "segmented_newspaper_images/"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

num_images_processed = 0
start = time.time()

print(f"Starting processing at {start} time")

for NEWSPAPER_NAME in NEWSPAPER_DIRECTORY_NAMES:
    for SEGMENTED_NEWSPAPER_DIR in os.listdir(NEWSPAPER_NAME + SEGMENTED_NEWSPAPER_IMAGES_DIRECTORY_NAMES):
        if SEGMENTED_NEWSPAPER_DIR != "06":
            continue
        image_directory = NEWSPAPER_NAME + SEGMENTED_NEWSPAPER_IMAGES_DIRECTORY_NAMES + SEGMENTED_NEWSPAPER_DIR + "/"
        for image_filename in os.listdir(image_directory):
            output_filename = NEWSPAPER_NAME + GPT4O_PROCESSED_TEXT_DIRECTORY_NAME + SEGMENTED_NEWSPAPER_DIR + "/" + image_filename[:-4] + ".txt"
            # If that image has already been processed, skip its processing
            if os.path.exists(output_filename) \
                and os.path.isfile(output_filename):
                print(f"Text already processed for newspaper '{NEWSPAPER_NAME[:-1]}' number '{SEGMENTED_NEWSPAPER_DIR}', image '{image_filename}'... skipping")
                continue

            image_path = image_directory + image_filename
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

            with open(output_filename, "w") as of:
                of.write(response.choices[0].message.content + "\n\n")
            
            print(f"Just processed image {image_path}. File has now processed {num_images_processed} images.")
            num_images_processed += 1

end = time.time()
print(f"Finshed processing at {end} time")
print(f"Took {end - start} seconds to process {num_images_processed} images.")
print(f"AVERAGE TIME: {(end - start) / num_images_processed} sec/image")