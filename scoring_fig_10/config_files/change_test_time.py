import os
import yaml

# Directory containing the YAML files
directory_path = '.'  # Replace with the path to your directory

# New dates
new_start_date = "01/10/1980"
new_end_date = "30/09/2014"

# Loop through all files in the directory
for file_name in os.listdir(directory_path):
    if file_name.endswith('.yml'):
        file_path = os.path.join(directory_path, file_name)
        
        # Read the YAML file
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        # Check if the keys exist and update their values
        if 'test_start_date' in data:
            data['test_start_date'] = new_start_date
        if 'test_end_date' in data:
            data['test_end_date'] = new_end_date

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            yaml.safe_dump(data, file)
        print(f"Updated: {file_path}")
