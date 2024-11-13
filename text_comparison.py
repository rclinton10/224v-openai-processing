# This file compares the processed text to the ground truth text and dumps
# the results to a json file

import os
import re
import diff_match_patch as dmp_module # CREDIT TO https://github.com/google/diff-match-patch?tab=readme-ov-file
import json

PROCESSED_TEXT_DIRECTORY_NAME = "BLN600Dataset/ProcessedText/"
GROUND_TRUTH_DIRECTORY_NAME = "BLN600Dataset/GroundTruth/"

def load_and_clean_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = re.sub(r'[\n]', ' ', text)  # Remove newlines, replace with spaces
    text = re.sub(r'[_]', '', text)    # Remove underscores (used for page breaks)
    text = re.sub(r'’', '\'', text)    # Make all quotation marks consistent
    text = text.rstrip()               # Remove any trailing spaces
    return text

ground_truth_files = sorted([f for f in os.listdir(GROUND_TRUTH_DIRECTORY_NAME)])
comparison_files = sorted([f for f in os.listdir(PROCESSED_TEXT_DIRECTORY_NAME)])

def count_character_differences(comp_text, truth_text):
    '''
    The diff_main() function outputs an array of duples, where the first element in the
    duple is 0, -1, or 1, and the second element in the duple is a string of text.
    If the first element is -1, the string was found in truth_text and not comp_text. 
    If the first element is 1, the sting was found in comp_text and not truth_text.
    If the first element is 0, the string was found in both truth_text and comp_text.

    We find the number of entries in the diff_main() array that have a first
    element of -1 or 1 and count how many characters of difference there are accross 
    these instances.
    '''
    dmp = dmp_module.diff_match_patch()
    diff = dmp.diff_main(truth_text, comp_text)

    diff_char_count = 0
    for entry in diff:
        if entry[0] != 0: # We found a string where the two texts differed
            diff_char_count += len(entry[1])

    return diff_char_count

results = []
# Compare each file in comparison_files to its corresponding ground truth file
for comp_file, truth_file in zip(comparison_files, ground_truth_files):
    comp_text = load_and_clean_text(os.path.join(PROCESSED_TEXT_DIRECTORY_NAME, comp_file))
    truth_text = load_and_clean_text(os.path.join(GROUND_TRUTH_DIRECTORY_NAME, truth_file))

    differences = count_character_differences(comp_text, truth_text)
    print(f"# of character differences in {comp_file} between ground truth and processed text: {differences} chars.")
    
    results.append({
        "file_name": comp_file,
        "ground_truth_text_length": len(truth_text),
        "num_of_character_differences": differences
    })

# Output the following to a json: the txt file name, the length of the ground truth file,
# and the number of character differences between ground truth text and processed text.
with open("text_comparison_results.json", "w", encoding="utf-8") as json_file:
    json.dump(results, json_file, indent=4)

print(f"Differences written to text_comparison_results.json")