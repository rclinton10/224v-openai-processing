import pytesseract
from PIL import Image
import os
import time

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    # psm - page segmentation model
    # oem - OCR engine model
    text = pytesseract.image_to_string(img, config='--psm 4 --oem 1') # psm 3 wasn't bad
    print(text)
    return text

input_base_dir = "evaluation_data"
output_base_dir = "baseline_pipeline_output"

num_images_processed = 0
start_time = time.time()

for category in os.listdir(input_base_dir):
    category_path = os.path.join(input_base_dir, category)
    if os.path.isdir(category_path):
        for image in os.listdir(category_path):
            if image == ".DS_Store":
                continue
            image_path = os.path.join(category_path, image)
            print(f"Processing: {image_path}")

            extracted_text = extract_text_from_image(image_path)

            output_category_dir = os.path.join(output_base_dir, category)
            output_file_path = os.path.join(output_category_dir, image)
            output_file_path = output_file_path[:-4] + ".txt"

            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, "w") as output_file:
                output_file.write(extracted_text)

            print(f"Text extracted and saved for {image_path}")
            num_images_processed += 1
        if num_images_processed == 3:
            exit()

end_time = time.time()
print(f"Processed {num_images_processed} images in {end_time - start_time} seconds.")
print(f"Average time per image: {(end_time - start_time) / num_images_processed:.2f} seconds.")