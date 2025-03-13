#!/bin/bash

# Set the base directory
base_dir="./runs"

# Loop through each subdirectory in the base directory
for sub_dir in "$base_dir"/*; do
    if [ -d "$sub_dir" ]; then  # Check if it's a directory
        sub_dir_name=$(basename "$sub_dir")  # Extract the subdirectory name
        echo "Evaluating model in: $sub_dir_name"

        # Run the evaluation command
        nh-run evaluate --run-dir "$base_dir/$sub_dir_name"
    fi
done
