"""
File: azure_segmentation.py
-----
Purely for segmenting a newspaper page into smaller images
"""
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from PIL import Image

def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join([f"[{p.x}, {p.y}]" for p in polygon])

def filter_small_bboxes(lines, min_width=50, min_height=20):
    filtered_lines = []
    for line in lines:
        if line.polygon:
            x_coords = [point.x for point in line.polygon]
            y_coords = [point.y for point in line.polygon]
            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)
            if width >= min_width and height >= min_height:
                filtered_lines.append(line)
    return filtered_lines

def group_bounding_boxes(lines, proximity_threshold=30):
    grouped_lines = []
    current_group = {"content": "", "polygon": []}

    for line in lines:
        line_polygon = line.polygon
        if current_group["content"]:
            last_y = (
                max([point.y for point in current_group["polygon"]])
                if current_group["polygon"]
                else 0
            )
            if abs(last_y - line_polygon[0].y) <= proximity_threshold:
                current_group["content"] += " " + line.content
                current_group["polygon"].extend(line_polygon)
            else:
                grouped_lines.append(current_group)
                current_group = {"content": line.content, "polygon": line_polygon}
        else:
            current_group = {"content": line.content, "polygon": line_polygon}

    if current_group["content"]:
        grouped_lines.append(current_group)

    return grouped_lines

def save_segments_as_images(input_image, segments, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with Image.open(input_image) as img:
        img_width, img_height = img.size  # Get dimensions of the original image
        segment_counter = 1  # Maintain sequential numbering for saved segments

        for segment in segments:
            if not segment["polygon"]:
                continue

            x_coords = [point.x for point in segment["polygon"]]
            y_coords = [point.y for point in segment["polygon"]]

            left = max(0, min(x_coords))
            upper = max(0, min(y_coords))
            right = min(img_width, max(x_coords))
            lower = min(img_height, max(y_coords))

            # Ensure the bounding box has valid dimensions
            if right <= left or lower <= upper:
                continue

            width = right - left
            height = lower - upper
            aspect_ratio = width / height if height > 0 else 0

            # Skip segments that are likely lines (very narrow or small area)
            if width < 10 or height < 10 or width * height < 50 or aspect_ratio > 10 or aspect_ratio < 0.1:
                continue

            bbox = (left, upper, right, lower)
            cropped_img = img.crop(bbox)
            output_path = os.path.join(output_dir, f"segment_{segment_counter}.png")
            cropped_img.save(output_path)
            print(f"Saved segment {segment_counter} to {output_path}")
            segment_counter += 1

def analyze_layout(input_file, output_dir):
    endpoint = os.environ["DI_ENDPOINT"]
    key = os.environ["DI_KEY"]
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    with open(input_file, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-layout", document=f
        )
    result = poller.result()

    segments = []
    for page in result.pages:
        print(f"Processing Page {page.page_number}")

        # Step 1: Filter small bounding boxes
        lines = filter_small_bboxes(page.lines)

        # Step 2: Group bounding boxes by sections/articles
        grouped_lines = group_bounding_boxes(lines)

        for group in grouped_lines:
            segments.append(
                {"content": group["content"], "polygon": group["polygon"]}
            )

    save_segments_as_images(input_file, segments, output_dir)

if __name__ == "__main__":
    input_dir = "evaluation_data/handwritten"
    output_dir = "azure_segmented_images/handwritten"

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".png") or file_name.endswith(".jpg"):
            input_file = os.path.join(input_dir, file_name)
            output_subdir = os.path.join(output_dir, os.path.splitext(file_name)[0])
            print(f"Processing {input_file}...")
            try:
                analyze_layout(input_file, output_subdir)
            except Exception as error:
                print(f"Error processing {input_file}: {error}")
