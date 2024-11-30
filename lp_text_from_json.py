import json
import os

PARENT_FOLDER = "layout_parser_full_outputs"

for subdir, dirs, files in os.walk(PARENT_FOLDER):
    for file in files:
        json_path = os.path.join(subdir, file)

        output_path = json_path[len(PARENT_FOLDER) + 1:]
        output_path = output_path[:-5]  # Remove the file extension
        output_path = "layout_parser_pipeline_output/" + output_path + ".txt"

        try:
            with open(json_path, 'r') as file:
                data = json.load(file)

            text = data['fullTextAnnotation']['text']

            with open(output_path, "w") as of:
                of.write(text + "\n")
            
            print(f"Just wrote response to {output_path}")

        except Exception as e:
            print(f"Error extracting from the following Json file: {json_path}. Error message: {e}. Skipping this file.")
