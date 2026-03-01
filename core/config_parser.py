"""
Configurations parser for the application.
"""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load and parse the YAML configuration file.
    
    Args:
        file_path (str): The path to the config file.
        
    Returns:
        Dict[str, Any]: The parsed configuration dictionary.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found at {path}")
        
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    return config

def get_lab_config(config: Dict[str, Any], lab_id: int) -> Dict[str, Any]:
    """
    Retrieve the configuration for a specific lab ID.
    
    Args:
        config (Dict[str, Any]): The full configuration dictionary.
        lab_id (int): The ID of the lab to retrieve.
        
    Returns:
        Dict[str, Any]: The configuration for the specified lab.
    """
    labs = config.get("labs", [])
    for lab in labs:
        if lab.get("id") == lab_id:
            return lab
            
    raise ValueError(f"Lab with ID {lab_id} not found in configuration.")
