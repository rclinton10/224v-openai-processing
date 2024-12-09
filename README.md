# Historical Newspaper Processing

This repository contains the code, dataset, and evaluation tools used in our final project for CS224V, to tackle the challenges of extracting text from historical newspapers. Our goal is to develop a robust pipeline for segmenting and extracting text from complex historical newspaper layouts, ensuring that they remain accessible to researchers, educators, and the general public.

## Project Overview
Historical newspapers provide invaluable cultural and anecdotal insights, but their digitization is hindered by challenges such as:
- Complex layouts and small fonts
- Faded or degraded scans
- Non-linear reading orders

We created a custom dataset and evaluated several text extraction tools to address these challenges. This repository includes:
1. Code for implementing and evaluating text extraction pipelines.
2. The custom dataset used for testing, sourced from a variety of different historical archives. 

## Repository Structure
- **`evaluation_data/`**: Contains the dataset of historical newspaper images categorized by layout complexity (e.g., simple, moderate, complex, handwritten).
- **`baseline_pipeline.py`**: Baseline pipeline using PyTesseract for OCR.
- **`azure_pipeline.py`**: Implementation using Azure Document Intelligence.
- **`layout_parser_pipeline.py`**: Code for Layout Parser integration.
- **`azure_segmentation.py`** and **`google-vision-api.py`**: Combines Azure and Google Vision for handwritten text extraction.

## Dataset Details
Our custom evaluation dataset includes 39 images categorized into the following layout types:
- **Simple Layout**: Has a straightforward reading order, clear and simple text, and minimal or no images, making it the easiest to interpret.
- **Moderate Layout**: Includes some small text, a few potential reading orders, and a moderate number of images, offering a balance of complexity and readability.
- **Complex Layout**: Features very small text, numerous columns, multiple potential reading orders, and a high density of images, making interpretation challenging.
- **Faded/Ripped**: A significant portion of the text is difficult to read due to fading or degradation, requiring additional processing to extract the content accurately.
- **Handwritten**: A large portion of the text is handwritten, adding a layer of complexity to interpretation.
- **Image-Heavy**: Includes many images, often occupying a significant portion of the newspaper’s layout, which can interfere with text extraction and layout analysis.
- **Comics**: Illustrated panels with unique layouts and text.

## Key Pipelines
- **PyTesseract**: Baseline OCR using Google’s Tesseract engine.
- **Azure Document Intelligence**: Advanced tool for layout analysis and text extraction.
- **Layout Parser**: Open-source framework integrated with Google Vision API for robust processing.
- **Hybrid (Azure + Google Vision)**: Designed for handwritten text.

## Results
- Layout Parser was the most robust tool overall, balancing cost, runtime, and text accuracy/ordering.

## How to Run
1. Clone this repository:  
   ```bash
   git clone https://github.com/rclinton10/cs224v-newspaper-processing.git
   cd cs224v-newspaper-processing
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Example of running a pipeline:
   ```bash
   python3 baseline_pipeline.py
   ```

## Contact

We hope you are able to take something away from our project! Please feel free to reach out if you have any questions or feedback for us:

- **Rachel Clinton**: [rclinton@stanford.edu](mailto:rclinton@stanford.edu)
- **Jeong Shin**: [jyshin@stanford.edu](mailto:jyshin@stanford.edu)
