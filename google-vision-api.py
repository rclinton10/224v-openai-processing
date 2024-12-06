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

        if response.error.message:
            raise Exception(response.error.message)

        return texts[0].description.strip() if texts else ""
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def process_directory(parent_dir, output_dir):
    if not os.path.isdir(parent_dir):
        print(f"Directory {parent_dir} does not exist.")
        exit(1)

    os.makedirs(output_dir, exist_ok=True)

    for subdir in os.listdir(parent_dir):
        subdir_path = os.path.join(parent_dir, subdir)
        if os.path.isdir(subdir_path):
            print(f"\nProcessing directory: {subdir}")

            output_file_path = os.path.join(output_dir, f"{subdir}.txt")

            try:
                with open(output_file_path, "w") as outfile:
                    for filename in sorted(
                        os.listdir(subdir_path),
                        key=lambda x: int(os.path.splitext(x)[0]) if x.split('.')[0].isdigit() else float('inf')
                    ):
                        if filename.lower().endswith(".png"):
                            image_path = os.path.join(subdir_path, filename)
                            extracted_text = extract_text_with_google_vision(image_path)
                            if extracted_text:
                                outfile.write(extracted_text + " ")

            except Exception as e:
                print(f"Error processing directory {subdir}: {e}")

if __name__ == "__main__":
    parent_dir = "azure_segmented_images/faded_ripped"
    output_dir = "google-vision-api-output"

    process_directory(parent_dir, output_dir)
