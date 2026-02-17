import json
import os

# Get absolute path to config.json ensuring it works from any directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

def load_threshold():
    """Reads the threshold from config.json"""
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config.get("threshold", 0.25)
    except FileNotFoundError:
        print(f"Error: Config file not found at {CONFIG_PATH}")
        return 0.25

def update_threshold(new_threshold):
    """Updates the threshold in config.json"""
    try:
        # Validate input
        if not (0.0 <= new_threshold <= 1.0):
            print("Error: Threshold must be between 0.0 and 1.0")
            return False

        # Read existing config to preserve other keys if any
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update value
        config["threshold"] = new_threshold
        
        # Write back to file
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
            
        print(f"Threshold successfully updated to {new_threshold}")
        return True
    except Exception as e:
        print(f"Error updating threshold: {e}")
        return False

if __name__ == "__main__":
    # Test the functions
    current = load_threshold()
    print(f"Current Threshold: {current}")