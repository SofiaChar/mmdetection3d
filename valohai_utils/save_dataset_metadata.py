import json
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Save metadata for dataset zip file.')
parser.add_argument('--file_path', type=str, help='Path to the zip file')
parser.add_argument('--dataset_name', type=str, help='Name of the dataset')
parser.add_argument('--dataset_version', type=str, help='Version of the dataset')

# Parse the arguments
args = parser.parse_args()

# Construct the metadata
metadata = {
    "valohai.dataset-versions": [f"dataset://{args.dataset_name}/{args.dataset_version}"]
}

# Save the metadata to a .metadata.json file
metadata_path = f'{args.file_path}.metadata.json'
with open(metadata_path, 'w') as outfile:
    json.dump(metadata, outfile)

print(f'Metadata saved at {metadata_path}')
