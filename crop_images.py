import json
from PIL import Image
import fitz
import io
import os

jp2_file_path = '1827_raw_images/00.jp2'  # Raw image path
json_file_path = '1827_json/1827_00.json'  # JSON with metadata about the article/newspaper


with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

# Sort bounding boxes for left-to-right, top-to-bottom reading order
sorted_bboxes = sorted(
    json_data["bboxes"],
    key=lambda b: (b["bbox"]["y0"], b["bbox"]["x0"])
)

# Openining the JP2 file
with fitz.open(jp2_file_path) as jp2_doc:
    page = jp2_doc[0]  # Assuming a single page
    pix = page.get_pixmap()

    temp_image_path = 'temp_image.png'
    pix.save(temp_image_path)

    image = Image.open(temp_image_path)

# Iterate over each sorted bounding box and crop the images
for index, bbox_data in enumerate(sorted_bboxes):
    bbox = bbox_data["bbox"]
    x0, y0, x1, y1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]

    # Crop the region of the image based on bbox
    cropped_image = image.crop((x0, y0, x1, y1))

    # Save the cropped image with sequential filenames
    output_filename = f"{str(index + 1).zfill(3)}_{bbox_data['class']}.png"
    cropped_image.save(output_filename, "PNG")

    print(f"Cropped image saved as {output_filename}")

os.remove(temp_image_path)
