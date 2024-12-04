import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config='--psm 1 --oem 1')
    print(text)
    return text

extract_text_from_image("/Users/rachelclinton/Desktop/224v-openai-processing/evaluation_data/moderate_layout/loc_anchoragedaily_31oct1916.png")