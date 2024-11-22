import pickle
import json
import numpy as np

# Function to convert numpy types to native Python types
def convert_to_python_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, dict):
        return {convert_to_python_types(k): convert_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_types(i) for i in obj]
    else:
        return obj

# Load the pkl file
with open('./household_attributes.pkl', 'rb') as f:
    household_attributes = pickle.load(f)

# Convert keys and values to Python native types
household_attributes_converted = {int(k): convert_to_python_types(v) for k, v in household_attributes.items()}

# Write to JSON file
with open('./household_attributes.json', 'w') as json_file:
    json.dump(household_attributes_converted, json_file)
