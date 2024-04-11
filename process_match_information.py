import json

main()

def main():
    # Accept user input for the file name
    file_name = input("Enter the file path: ")

    # Open the file for processing
    with open(file_path, "r") as file:
        # Process the file contents
        match_data = json.load(file)

    match_information = process_match_data(match_data)

    # Output the processed data to a new file
    output_file_path = file_name + "_process"
    with open(output_file_path, "w") as output_file:
        json.dump(match_information, output_file)
        
def process_match_data(match_data):
    match_information = {}
    
    match_information["match_id"] = match_data["match_id"]
    
    return match_information