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
    with open(input_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-read", document=f
        )
    result = poller.result()

    with open(output_file_path, "w") as output_file:
        for page in result.pages:
            for line in page.lines:
                output_file.write(line.content + "\n")


def main():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["DI_ENDPOINT"]
    key = os.environ["DI_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # # FOR INDIVIDUAL FILES
    # input_path = "evaluation_data/complex_layout/jaic__granada_pioneer_03nov1944.jp2"
    # if not os.path.isfile(input_path):
    #     print("The specified file does not exist.")
    #     return

    # output_dir = "output"
    # os.makedirs(output_dir, exist_ok=True)

    # if input_path.lower().endswith(".jp2"):
    #     file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    #     print("File size: ", file_size_mb)

    #     start_time = time.time()

    #     converted_path = convert_to_supported_format(input_path)

    #     output_file_name = os.path.splitext(os.path.basename(input_path))[0] + ".txt"
    #     output_file_path = os.path.join(output_dir, output_file_name)

    #     try:
    #         extract_text(converted_path, output_file_path, document_analysis_client)
    #         print(f"Text extraction complete. Saved to {output_file_path}")
    #     except Exception as e:
    #         print(f"Failed to process {input_path}: {e}")

    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     print(f"Processing time for {os.path.basename(input_path)}: {elapsed_time:.2f} seconds")
    #     print()

    #     os.remove(converted_path)
    # else:
    #     print("The specified file is not a .jp2 file.")

    # FOR DIRECTORIES
    input_dir = "evaluation_data/simple_layout"
    output_dir = "output/simple_layout"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        if filename.lower().endswith((".jp2", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".heif")):
            print(f"Processing: {filename}")

            start_time = time.time()

            if filename.lower().endswith(".jp2"):
                file_path = convert_to_supported_format(file_path)

            output_file_name = os.path.splitext(filename)[0] + ".txt"
            output_file_path = os.path.join(output_dir, output_file_name)

            try:
                extract_text(file_path, output_file_path, document_analysis_client)
                print(f"Text extraction complete for {filename}. Saved to {output_file_path}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Processing time for {filename}: {elapsed_time:.2f} seconds")
            print()

            if filename.lower().endswith(".jp2"):
                os.remove(file_path)


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
