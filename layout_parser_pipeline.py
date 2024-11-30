import layoutparser as lp
import cv2
import json
from google.protobuf import json_format
import os

ocr_agent = lp.GCVAgent.with_credential("linear-sight-413400-5ab3e8999caf.json", languages=['en'])

PARENT_FOLDER = "evaluation_data"

def resize_image(image, max_size=40 * 1024 * 1024):
    if image.size > max_size:
        # Calculate scaling factor
        scale_factor = (max_size / image.size) ** 0.5
        # Resize image proportionally
        new_width = int(image.shape[1] * scale_factor)
        new_height = int(image.shape[0] * scale_factor)
        image = cv2.resize(image, (new_width, new_height))
    return image

for subdir, dirs, files in os.walk(PARENT_FOLDER):
    for image in files:
        image_path = os.path.join(subdir, image)

        # Generate output path based on input file path
        output_path = image_path[len(PARENT_FOLDER) + 1:]
        output_path = output_path[:-4]  # Remove the file extension
        output_path = "layout_parser_full_outputs/" + output_path + ".json"

        print(f"Trying image {image_path}")
        
        im = cv2.imread(image_path)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        im = resize_image(im)

        try:
            res = ocr_agent.detect(im, return_response=True)  # Returns an AnnotateImageResponse object

            # Convert the AnnotateImageResponse to JSON
            response_json = json_format.MessageToJson(res)
            response_json = json.loads(response_json)

            # Save the response to a JSON file
            with open(output_path, "w") as of:
                json.dump(response_json, of, indent=4)
                
            print(f"Just wrote response for image {image_path}")

        except Exception as e:
            print(f"Error during OCR for {image_path}: {e}. Skipping this file.")
