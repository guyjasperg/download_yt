import os
import re

def compare_and_remove_files(dir1, dir2):
    """
    Compares the contents of two directories. Removes files from dir2 that do not exist in dir1.
    
    Args:
        dir1 (str): Path to the first directory.
        dir2 (str): Path to the second directory.
    """
    try:
        # List files in both directories
        files_in_dir1 = set(os.listdir(dir1))
        files_in_dir2 = set(os.listdir(dir2))

        # Compare the files in both directories
        files_to_remove_from_dir2 = files_in_dir2 - files_in_dir1

        if files_to_remove_from_dir2:
            print(f"Files to remove from {dir2}: {files_to_remove_from_dir2}")

            for filename in files_to_remove_from_dir2:
                file_path = os.path.join(dir2, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed: {filename}")
                else:
                    print(f"Skipping: {filename} (not a file)")

        else:
            print("No files to remove. Both directories are identical.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# dir1_path = "/Users/guyjasper/Pictures/MyPictures/2024-12-14 [CIC] Family Day copy/JPG_10X12"  # Replace with your first directory path
# dir2_path = "/Users/guyjasper/Pictures/MyPictures/2024-12-14 [CIC] Family Day copy/Upload"  # Replace with your second directory path
# compare_and_remove_files(dir1_path, dir2_path)

def batch_remove_keywords_case_insensitive(directory, keywords):
    """
    Removes specified keywords from filenames in a directory, case-insensitively,
    while preserving the original case for non-matching parts of the filename.

    Parameters:
        directory (str): Path to the directory containing the files to process.
        keywords (list of str): List of keywords to remove from filenames.

    Returns:
        None: The filenames are updated in place.
    """
    # Check if the provided directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"The provided path is not a directory: {directory}")

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Construct the full path to the file
        full_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(full_path):
            continue

        # Remove keywords from the filename case-insensitively
        new_name = filename
        for keyword in keywords:
            # Create a regex pattern that is case-insensitive
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            new_name = pattern.sub("", new_name)

        # Strip leading/trailing whitespace and construct the new full path
        new_name = new_name.strip()
        new_full_path = os.path.join(directory, new_name)

        # Rename the file if the name has changed
        if new_name != filename:
            os.rename(full_path, new_full_path)

    print(f"Processed all files in directory: {directory}")

# Example usage:
# Replace with the path to your directory
directory_path = "/Users/guyjasper/Documents/Guy/Projects/Python/HelloWorld/NEW_SONGS" 

# List of keywords to remove from filenames
keywords_to_remove = [
    "_with_audio",
    " | karaoke version | karafun",
    " | karaoke version",
    " KARAOKE VERSION",
    " (KARAOKE)",
    "[KARAOKE] ",
    " [KARAOKE]",
    "- as popularized by",
    "🎤🎵",
    " (Karaoke Version)",
    " ( Karaoke Version )",
    " (Karaoke  Lower Key)",
    " (Karaoke With Lyrics)",
    " (Hd Karaoke)",
    " (Karaoke Studio Version)",
    "Karaoke version in the style of ",
    "in the style of ",
    " (KARAOKE HD)",
    " - from Zoom Karaoke",
    " (KARAOKE PIANO VERSION)",
    "(Karaoke Acoustic Instrumental)"
    ]

# if __name__ == "__main__":
#     batch_remove_keywords_case_insensitive(directory_path, keywords_to_remove)

def remove_keywords(filename, keywords=None):
    if keywords is None:
        keywords = []

    new_name = filename
    keywordtoremove = keywords_to_remove if keywords == "" else keywords

    for keyword in keywordtoremove:
        # Create a regex pattern that is case-insensitive
        # pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        pattern = r"\b" + re.escape(keyword) + r"\b"
        # new_name = pattern.sub("", new_name)
        new_name = re.sub(pattern, "", new_name, flags=re.IGNORECASE).strip()

    # Strip leading/trailing whitespace and construct the new full path
    new_name = new_name.strip()
    return " ".join(new_name.split())

def fix_filenames_in_directory(directory):
    """
    Adjusts all filenames in the specified directory so that the start of each word is capitalized.

    Parameters:
        directory (str): The path to the directory containing the files to process.

    Returns:
        None: The filenames are updated in place.
    """
    # Check if the provided directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"The provided path is not a directory: {directory}")
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Construct the full path to the file
        full_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(full_path):
            continue

        # Separate the filename and the extension
        name, ext = os.path.splitext(filename)
        
        # Capitalize the start of each word in the main filename
        new_name = name.title()
        
        # Construct the new full path
        new_full_path = os.path.join(directory, f"{new_name}{ext}")

        # Rename the file
        os.rename(full_path, new_full_path)

    print(f"Processed all files in directory: {directory}")

# directory_path = "/Users/guyjasper/Documents/Guy/Projects/Python/HelloWorld/DOWNLOADS" 
# fix_filenames_in_directory(directory_path)

def remove_duplicate_in_directory(directory):
    print("+remove_duplicate_in_directory")

    # Check if the provided directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"The provided path is not a directory: {directory}")
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Construct the full path to the file
        full_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(full_path):
            continue

        # Separate the filename and the extension
        name, ext = os.path.splitext(filename)


        if str(filename).find("_2.jpg") != -1:
            #remove similar file without the _2 in filename
            dup_file = os.path.join(directory, f"{str(filename).replace("_2.jpg",".jpg")}")
            if os.path.isfile(dup_file):
                os.remove(dup_file) 
                print(f"Removed file: {dup_file}")

    print(f"Processed all files in directory: {directory}")
    print("-remove_duplicate_in_directory")

#remove invalid characters from file name
def CleanFilename(filename):
    #TBD
    return str(filename).replace('/',' ')

if __name__ == "__main__":
    directory_path = "/Users/guyjasper/Desktop/Don & Irish/JPG_8X12" 
    remove_duplicate_in_directory(directory_path)

