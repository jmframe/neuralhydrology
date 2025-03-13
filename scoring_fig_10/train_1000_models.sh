#!/bin/bash

# Loop through config values from 1000 to 2000
for i in {1000..2000}
do
  # Run the command with the corresponding config file
  nh-run train --config-file ./config_files/config_leaf_${i}.yml
done

