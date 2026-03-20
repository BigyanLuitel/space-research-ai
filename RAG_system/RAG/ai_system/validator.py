SPACE_KEYWORDS = [
     "satellite", "orbit", "orbital", "trajectory",
    "latitude", "longitude", "altitude", "elevation",
    "spacecraft", "rocket", "launch", "payload",
    "velocity", "acceleration", "thrust", "telemetry",
    "planet", "asteroid", "comet", "stellar", "galaxy",
]

def is_relevant_to_space(text):
    return {
        "is_relevant": any(keyword in text.lower() for keyword in SPACE_KEYWORDS),
        "reason": "Contains space-related keywords." 
        if any(keyword in text.lower() for keyword in SPACE_KEYWORDS) 
        else "No space-related keywords found."
        
    }