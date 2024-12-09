import json
import cv2
import os

def resize_image(image, max_size=40 * 1024 * 1024):
    if image.size > max_size:
        scale_factor = (max_size / image.size) ** 0.5
        new_width = int(image.shape[1] * scale_factor)
        new_height = int(image.shape[0] * scale_factor)
        image = cv2.resize(image, (new_width, new_height))
    return image

def crop_image_from_json(json_file_path, image_file_path, output_folder):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    im = cv2.imread(image_file_path)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im = resize_image(im)

    layout_type = json_file_path.split(os.path.sep)[1]
    image_name = os.path.splitext(os.path.basename(image_file_path))[0]

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page in data['fullTextAnnotation']['pages']:
        i = 0
        for block in page['blocks']:
            vertices = block['boundingBox']['vertices']

            if len(vertices) < 4:
                print(f"Skipping block with invalid vertices: {vertices}")
                continue  # Skip blocks with invalid or missing vertices

            # Attempt to extract coordinates
            try:
                top_left_coordinate = vertices[0]
                bottom_right_coordinate = vertices[2]
                
                # Ensure 'x' and 'y' keys exist in the coordinates
                x_1 = top_left_coordinate.get('x', None)
                y_1 = top_left_coordinate.get('y', None)
                x_2 = bottom_right_coordinate.get('x', None)
                y_2 = bottom_right_coordinate.get('y', None)

                # Check if coordinates are missing
                if None in (x_1, y_1, x_2, y_2):
                    print(f"Skipping block with missing coordinates: {top_left_coordinate} to {bottom_right_coordinate}")
                    continue
            
            except Exception as e:
                print(f"Error accessing coordinates in block: {e}")
                continue

            x_1 = max(0, min(x_1, im.shape[1]))  # Ensure within width
            y_1 = max(0, min(y_1, im.shape[0]))  # Ensure within height
            x_2 = max(0, min(x_2, im.shape[1]))  # Ensure within width
            y_2 = max(0, min(y_2, im.shape[0]))  # Ensure within height

            cropped_img = im[y_1:y_2, x_1:x_2]  # y-axis is first, then x-axis

            if cropped_img.size == 0:
                print(f"Empty cropped image for block {i} with coordinates {top_left_coordinate} to {bottom_right_coordinate}")
                continue  # Skip empty crops

            output_dir = os.path.join(output_folder, layout_type, image_name)
            os.makedirs(output_dir, exist_ok=True)  # Create folder if it doesn't exist

            cropped_img_name = f"{output_dir}/{i}.png"
            i += 1
            cv2.imwrite(cropped_img_name, cropped_img)
            print(f"Saved cropped image: {cropped_img_name}")

LAYOUT_PARSER_FOLDER = "results/layout_parser_full_outputs"
EVAL_DATA_FOLDER = "evaluation_data"
OUTPUT_FOLDER = "results/layout_parser_segmented_images"
VALID_EXTENSIONS = [".jp2", ".png", ".jpg"]

for subdir, dirs, files in os.walk(LAYOUT_PARSER_FOLDER):
    for file in files:
        if file.endswith('.json'):
            json_file_path = os.path.join(subdir, file)
            
            # Construct the corresponding image file path in the evaluation_data folder
            image_file_path = os.path.join(EVAL_DATA_FOLDER, json_file_path[len(LAYOUT_PARSER_FOLDER) + 1:-5])  # Remove .json extension

            # Try each possible image extension
            image_found = False
            for ext in VALID_EXTENSIONS:
                image_path_with_ext = image_file_path + ext
                if os.path.exists(image_path_with_ext):
                    image_file_path = image_path_with_ext
                    image_found = True
                    break  # Image found, no need to check further extensions

                if not image_found:
                    print(f"Error: No image found for JSON file {json_file_path}")
                    continue  # Skip this JSON file if no corresponding image is found
            
            crop_image_from_json(json_file_path, image_file_path, OUTPUT_FOLDER)
