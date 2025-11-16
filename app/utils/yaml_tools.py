import os
import yaml

def save_yaml(data, filepath):
    """Save dictionary data to a YAML file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False)

def load_yaml(filepath):
    """Load YAML file and return its contents as a dictionary."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def list_yaml_files(directory):
    """Return list of YAML files in the given directory."""
    return [f for f in os.listdir(directory) if f.endswith(('.yaml', '.yml'))]
