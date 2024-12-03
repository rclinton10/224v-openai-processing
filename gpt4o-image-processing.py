# This file goes through all of the images in our dataset and uses GPT-4o to 
# determine the text that is in the image. It stores each text file in 
# [newspaperName]/gpt4o_processed_text/[newspaperNumber/[imageFileName].txt
from openai import OpenAI
import base64
import os
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL="gpt-4o"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

num_images_processed = 0
start = time.time()

print(f"Starting processing at {start} time")

import os

# Define input and output base directories
input_base_dir = "layout_parser_segmented_images"
output_base_dir = "layout_parser_open_ai_pipeline_output"

num_images_processed = 0
for category in os.listdir(input_base_dir):
    # We only run this pipeline on faded_ripped and handwritten text
    if category != "handwritten":
        continue
    category_path = os.path.join(input_base_dir, category)
    if os.path.isdir(category_path): 
        for image_folder in os.listdir(category_path):
            image_folder_path = os.path.join(category_path, image_folder)

            print(f"Current processing the image at path {image_folder_path}")
            if os.path.isdir(image_folder_path):
                for image_file in sorted(os.listdir(image_folder_path)):  # Sort to maintain file order
                    image_file_path = os.path.join(image_folder_path, image_file)
                    full_image_text = ""
                    if os.path.isfile(image_file_path) and image_file.endswith(".png"):
                        base64_image = encode_image(image_file_path)
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that can look at an image that is faded or has handwritten text \
                                    and accurately tell me all of the text on the image using logic. Help me determine the text on the following images."},
                                {"role": "user", "content": [
                                    {"type": "text", "text": "What is all of the text on this newspaper clip? I just need the raw text, nothing else."},
                                    {"type": "image_url", "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"}
                                    }
                                ]}
                            ],
                            temperature=0.0,
                        )

                        full_image_text += response.choices[0].message.content
                        num_images_processed += 1
                        print(full_image_text)
                        # print(f"{num_images_processed} images have been processed")

                # Prepare output folder path
                output_category_dir = os.path.join(output_base_dir, category)
                output_folder_dir = os.path.join(output_category_dir, image_folder)
                os.makedirs(output_folder_dir, exist_ok=True)

                output_file_path = os.path.join(output_folder_dir, f"{image_folder}.txt")
                with open(output_file_path, "w") as output_file:
                    output_file.write(full_image_text) 

                print(f"Processed {image_folder} in {category}, output saved to {output_file_path}")
                exit()

end = time.time()
print(f"Finshed processing at {end} time")
print(f"Took {end - start} seconds to process {num_images_processed} images.")
print(f"AVERAGE TIME: {(end - start) / num_images_processed} sec/image")
