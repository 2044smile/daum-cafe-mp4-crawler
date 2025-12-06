"""Filename utilities"""


def sanitize_filename(filename):
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace problematic characters
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
    }
    
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    return filename
