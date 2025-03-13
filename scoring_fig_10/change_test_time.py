import os
import yaml

# Directory containing the run directories
runs_directory = './runs'  # Replace with the path to your runs directory

# New dates
new_start_date = "01/10/1980"
new_end_date = "30/09/2014"

# Loop through all run directories
for run_dir in os.listdir(runs_directory):
    config_path = os.path.join(runs_directory, run_dir, 'config.yml')
    
    # Check if config.yml exists in the run directory
    if os.path.isfile(config_path):
        # Read the YAML file
        with open(config_path, 'r') as file:
            data = yaml.safe_load(file)

        # Check if the keys exist and update their values
        if 'test_start_date' in data:
            data['test_start_date'] = new_start_date
        if 'test_end_date' in data:
            data['test_end_date'] = new_end_date

        # Write the updated data back to the file
        with open(config_path, 'w') as file:
            yaml.safe_dump(data, file)
        print(f"Updated: {config_path}")
    else:
        print(f"Config file not found in: {os.path.join(runs_directory, run_dir)}")

