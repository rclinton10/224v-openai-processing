import os
from google.cloud import vision

client = vision.ImageAnnotatorClient()

def extract_text_with_google_vision(image_path):
    try:
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        response = client.text_detection(image=image)
        texts = response.text_annotations

        return texts[0].description.strip() if texts else ""
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

parent_dir = "azure_segmented_images/handwritten"

if not os.path.isdir(parent_dir):
    print(f"Directory {parent_dir} does not exist.")
    exit(1)

for subdir in os.listdir(parent_dir):
    subdir_path = os.path.join(parent_dir, subdir)
    if os.path.isdir(subdir_path):
        print(f"\nProcessing directory: {subdir}")
        
        output_file = f"{subdir}.txt"
        with open(output_file, "w") as outfile:
            for filename in sorted(os.listdir(subdir_path), key=lambda x: int(x.split('_')[-1].split('.')[0])):
                if filename.lower().endswith(".png"):
                    image_path = os.path.join(subdir_path, filename)
                    print(f"Processing: {filename}...")
                    
                    extracted_text = extract_text_with_google_vision(image_path)
                    
                    if extracted_text:
                        outfile.write(extracted_text + " ")

        print(f"Text extraction completed for {subdir}. Output saved to {output_file}.")
