import os
import time
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

    total_time = 0 
    total_directories = 0 

    for subdir in os.listdir(parent_dir):
        subdir_path = os.path.join(parent_dir, subdir)
        if os.path.isdir(subdir_path):
            print(f"\nProcessing directory: {subdir}")
            
            dir_start_time = time.time()

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

                dir_end_time = time.time()
                dir_elapsed_time = dir_end_time - dir_start_time
                print(f"Total processing time for directory {subdir}: {dir_elapsed_time:.2f} seconds.")

                total_time += dir_elapsed_time
                total_directories += 1

            except Exception as e:
                print(f"Error processing directory {subdir}: {e}")

    avg = total_time / total_directories
    print(f"Total time for all directories: {total_time:.2f} seconds.")
    print(f"Average processing time per directory: {avg:.2f} seconds.")

if __name__ == "__main__":
    parent_dir = "results/azure_segmented_images/handwritten"
    output_dir = "results/google-vision-api-output/handwritten" 

    process_directory(parent_dir, output_dir)
