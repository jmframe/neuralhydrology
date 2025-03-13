#!/bin/bash

# Create configuration files by replacing 'xxx' with numbers from 1000 to 2000
for i in $(seq 1000 2000); do
  # Define the new filename by replacing 'xxx' with the current number
  new_filename="config_leaf_${i}.yml"

  # Replace 'xxx' in the file contents with the current number and write to the new file
  sed "s/xxx/${i}/g" config_leaf_xxx.yml > "${new_filename}"
done

echo "Configuration files generated successfully."

