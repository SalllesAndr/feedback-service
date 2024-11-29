import uuid

def generate_custom_id(prefix: str) -> str:
    """
    Generates a custom ID with the given prefix and an 8-character UUID slice.
    
    Args:
        prefix (str): The prefix for the ID (e.g., 'stud', 'prof', 'feed').

    Returns:
        str: The generated custom ID.
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"
