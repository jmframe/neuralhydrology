import os

# Path to the directory containing the CSV files
csv_dir = "/home/jmframe/data/CAMELS_US/hourly/aorc_hourly/"

# Path to the file containing the basin IDs
basin_list_file = "/home/jmframe/data/CAMELS_US/list_515_camels_basins_aorc.txt"

# Paths to save the found and missing lists
found_file = "/home/jmframe/data/CAMELS_US/found_basins.txt"
missing_file = "/home/jmframe/data/CAMELS_US/missing_basins.txt"

# Read the basin IDs from the file
with open(basin_list_file, 'r') as f:
    basin_ids = [line.strip() for line in f.readlines()]

# Lists to store found and missing basin IDs
found_basins = []
missing_basins = []

# Check for each basin ID if the corresponding CSV file exists
for basin_id in basin_ids:
    csv_filename = f"{basin_id}_1980_to_2024_agg_rounded.csv"
    csv_path = os.path.join(csv_dir, csv_filename)
    
    if os.path.exists(csv_path):
        found_basins.append(basin_id)
    else:
        missing_basins.append(basin_id)

# Save the found basin IDs to a file
with open(found_file, 'w') as f_found:
    for basin_id in found_basins:
        f_found.write(f"{basin_id}\n")

# Save the missing basin IDs to a file
with open(missing_file, 'w') as f_missing:
    for basin_id in missing_basins:
        f_missing.write(f"{basin_id}\n")

print(f"Found basins saved to {found_file}")
print(f"Missing basins saved to {missing_file}")
