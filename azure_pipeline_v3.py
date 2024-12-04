"""
File: azure_pipeline_v3.py
-----
Code adapted from https://github.com/Azure-Samples/document-intelligence-code-samples/blob/v3.1(2023-07-31-GA)/Python(v3.1)/Layout_model/sample_analyze_layout.py
"""
import os
import time
from PIL import Image


def convert_to_supported_format(input_path):
    converted_path = input_path.replace(".jp2", ".jpg")
    image = Image.open(input_path)
    image = image.convert("RGB")
    image.save(converted_path, "JPEG", quality=85)
    return converted_path


def extract_text(input_path, output_file_path, document_analysis_client):
    """
    Uses Azure's prebuilt-layout model to extract text directly.
    """
    with open(input_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-layout",
            document=f
        )
    result = poller.result()
    with open(output_file_path, "w") as output_file:
        for page in result.pages:
            output_file.write(f"Page {page.page_number}\n")
            for line in page.lines:
                output_file.write(line.content + "\n")
            output_file.write("\n")
    print(f"Finished writing results for {input_path} to {output_file_path}")


def process_directory(input_dir, output_dir, document_analysis_client):
    print(f"Processing directory: {input_dir}")
    os.makedirs(output_dir, exist_ok=True)

    total_files = 0
    start_time = time.time()

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        if filename.lower().endswith((".jp2", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".heif")):
            total_files += 1

            if filename.lower().endswith(".jp2"):
                file_path = convert_to_supported_format(file_path)

            output_file_name = os.path.splitext(filename)[0] + ".txt"
            output_file_path = os.path.join(output_dir, output_file_name)

            try:
                extract_text(file_path, output_file_path, document_analysis_client)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

            if filename.lower().endswith(".jp2"):
                os.remove(file_path)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Done processing {os.path.basename(input_dir)}")
    print(f"Processed {total_files} PNG files. Total time: {elapsed_time:.2f} seconds.\n")
    return elapsed_time, total_files


def main():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ.get("DI_ENDPOINT")
    key = os.environ.get("DI_KEY")

    if not endpoint or not key:
        print("Azure endpoint or key not set! Exiting.")
        return

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    input_base_dir = "evaluation_data"
    output_base_dir = "azure_pipeline_output"

    total_time = 0
    total_files = 0

    for subdir in os.listdir(input_base_dir):
        input_dir = os.path.join(input_base_dir, subdir)
        output_dir = os.path.join(output_base_dir, subdir)

        if subdir == "faded_ripped":  # Skip the faded_ripped directory
            print(f"Skipping directory: {subdir}")
            continue

        if os.path.isdir(input_dir):
            print(f"Starting to process directory: {subdir}")
            elapsed_time, files_processed = process_directory(
                input_dir, output_dir, document_analysis_client
            )
            total_time += elapsed_time
            total_files += files_processed

    print(f"All directories processed. Total files: {total_files}. Total time: {total_time:.2f} seconds.")


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError

    try:
        main()
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
        if error.error is not None:
            print(f"Error code: {error.error.code}")
            print(f"Error message: {error.error.message}")
        else:
            print(f"Error message: {error.message}")
