import re, os

# List of keywords to remove from filenames
keywords_to_remove = [
    "Karaoke Version From Zoom Karaoke",
    "Original Karaoke Sound",
    "with audio",
    "karaoke version",
    "from zoom karaoke",
    "karaoke Instrumental",
    "without backing vocals",
    "full band karaoke",
    "stripped",
    "karaoke hd",
    "hd karaoke",
    "karafun",
    "karaoke",
    "as popularized by",
    "🎤🎵",
    "lower key",
    "with lyrics",
    "studio version",
    "version in the style of",
    "in the style of ",
    "piano version",
    "acoustic instrumental",
    ]

def remove_keywords2(filename, keywords=None):
    global keywords_to_remove
    
    if keywords is None:
        keywords = []

    new_name = filename
    keywordtoremove = keywords_to_remove if keywords == [] else keywords

    # clean invalid characters first
    invalid_chars = ['(', ')', '[', ']', '*', '_', '|']
    for char in invalid_chars:
        new_name = new_name.replace(char, ' ')
    
    # Remove double spaces
    while '  ' in new_name:
        new_name = new_name.replace('  ', ' ')

    for keyword in keywordtoremove:
        # Create a regex pattern that is case-insensitive
        pattern = r"\b" + re.escape(keyword) + r"\b" 
        new_name = re.sub(pattern, "", new_name, flags=re.IGNORECASE).strip()
        
    # Strip leading/trailing whitespace and construct the new full path
    new_name = new_name.strip()
    
    # Remove double spaces
    while '  ' in new_name:
        new_name = new_name.replace('  ', ' ')
    
    # Ensure the filename does not end with whitespace
    # Separate the filename and extension
    name, ext = re.match(r"^(.*?)(\.[^.]*?)?$", new_name).groups()
    
    # Strip white spaces from the name and extension
    name = name.strip()
    ext = ext.strip() if ext else ""
    
    # Combine the name and extension again
    new_name = f"{name}{ext}"
        
    return " ".join(new_name.split())

def remove_keywords(filename, keywords=None):
    global keywords_to_remove
    
    if keywords is None:
        keywords = []

    new_name = filename
    keywordtoremove = keywords_to_remove if keywords == [] else keywords

    # clean invalid characters first
    invalid_chars = ['(', ')', '[', ']', '*', '_', '|']
    for char in invalid_chars:
        new_name = new_name.replace(char, ' ')
    
    # Remove double spaces
    while '  ' in new_name:
        new_name = new_name.replace('  ', ' ')

    for keyword in keywordtoremove:
        # Create a regex pattern that is case-insensitive
        pattern = r"\b" + re.escape(keyword) + r"\b" 
        new_name = re.sub(pattern, "", new_name, flags=re.IGNORECASE).strip()
        
    # Strip leading/trailing whitespace and construct the new full path
    new_name = new_name.strip()
    
    # Remove double spaces
    while '  ' in new_name:
        new_name = new_name.replace('  ', ' ')
    
    # Ensure the filename does not end with whitespace
    # Separate the filename and extension
    name, ext = re.match(r"^(.*?)(\.[^.]*?)?$", new_name).groups()
    
    # Strip white spaces from the name and extension
    name = name.strip()
    ext = ext.strip() if ext else ""
    
    # Combine the name and extension again
    new_name = f"{name}{ext}"
        
    return " ".join(new_name.split())

def to_title_case(str):
  """
  Converts a string to title case with proper handling of keywords.

  Args:
      str: The input string.

  Returns:
      The string in title case.
  """
  keywords = [
      "and",
      "of",
      "the",
      "a",
      "to",
      "in",
      "is",
      "it",
      "for",
      "ni",
      "at",
      "na",
  ]

  try:
      words = str.lower().split() 
      title_case_words = [
          word if (keywords.count(word) > 0 and i > 0 and prev_word != "-") 
          else word.capitalize() 
          for i, (word, prev_word) in enumerate(zip(words, [" "] + words))
      ]
      return " ".join(title_case_words)

  except Exception as e:
      print(f"to_title_case: ERROR {e}")
      return str

def count_video_files(directory):
    """
    Counts the number of video files in the specified directory.

    Parameters:
        directory (str): The path to the directory containing the video files.

    Returns:
        int: The number of video files in the directory.
    """
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm']
    video_count = 0

    # Check if the provided directory exists
    if not os.path.isdir(directory):
        print(f"The provided path is not a directory: {directory}")
        return 0

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Construct the full path to the file
        full_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(full_path):
            continue

        # Skip hidden files
        if filename.startswith('.'):
            continue

        # Check if the file has a video extension
        if os.path.splitext(filename)[1].lower() in video_extensions:
            video_count += 1

    return video_count


temp = "/Users/guyjasper/Desktop/Temp/KARAOKE HITS V2"


# converted = to_title_case(remove_keywords(temp))
# print(temp)
# print(converted)

print('video files', count_video_files(temp))