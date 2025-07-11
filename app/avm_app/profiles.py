import json
import os

PROFILES_FILE = "profiles.json"

def load_profiles(default_min_conf_scores, default_desired_forms, default_max_fsd_values, default_available_forms):
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            profiles_data = json.load(f)
    else:
        profiles_data = {
            "profiles": {
                "Default": {
                    "min_conf_scores": default_min_conf_scores,
                    "desired_forms": default_desired_forms,
                    "max_fsd_values": default_max_fsd_values
                }
            },
            "available_forms": default_available_forms
        }
        save_profiles(profiles_data)
    
    return profiles_data

def save_profiles(profiles_data):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles_data, f, indent=4)

def load_profile(profiles_data, profile_name):
    profile = profiles_data["profiles"].get(profile_name, {})
    min_conf_scores = profile.get("min_conf_scores", {})
    desired_forms = set(profile.get("desired_forms", []))
    max_fsd_values = profile.get("max_fsd_values", {})
    available_forms = profiles_data.get("available_forms", list(desired_forms))
    return min_conf_scores, desired_forms, max_fsd_values, available_forms
