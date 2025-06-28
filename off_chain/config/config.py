import os
import yaml
 
"""
Load configuration settings from a YAML file.
"""

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(current_dir, 'configuration.yml')

with open(config_file, 'r') as file:
    config = yaml.safe_load(file)