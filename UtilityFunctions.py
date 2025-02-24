import os
import re
import sqlite3
import ffmpeg
import subprocess
import logging

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

# List of keywords to remove from filenames
keywords_to_remove = [
    "|",
    "[",
    "]",
    "(",
    ")",
    "_",
    "Karaoke Version From Zoom Karaoke",
    "_with_audio",
    "karaoke version",
    "from zoom karaoke",
    "karaoke Instrumental",
    "without backing vocals",
    "full band karaoke",
    "stripped",
    "karaoke hd",
    "karafun",
    "karaoke",
    "as popularized by",
    "🎤🎵",
    "lower key",
    "with lyrics",
    "hd karaoke",
    "studio version",
    "version in the style of",
    "in the style of ",
    "piano version",
    "acoustic instrumental",
    "()",
    "[]",
    "  ",
    ]

# if __name__ == "__main__":
#     batch_remove_keywords_case_insensitive(directory_path, keywords_to_remove)

def remove_keywords(filename, keywords=None):
    global keywords_to_remove
    
    if keywords is None:
        keywords = []

    new_name = filename
    keywordtoremove = keywords_to_remove if keywords == [] else keywords

    for keyword in keywordtoremove:
        # Create a regex pattern that is case-insensitive
        if "(" in keyword and ")" in keyword:
            pattern = r"\(" + re.escape(keyword[1:-1]) + r"\)" 
        else:
            pattern = r"\b" + re.escape(keyword) + r"\b" 
 
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
        print(name)
        
        # Capitalize the start of each word in the main filename
        new_name = to_title_case(remove_keywords(name))
        print(new_name)
        
        # # Construct the new full path
        new_full_path = os.path.join(directory, f"{new_name}{ext}")

        # # Rename the file
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

#remove invalid characters from file name
def CleanFilename(filename):
    #TBD
    return str(filename).replace('/',' ')

def replace_double_spaces(input_string):
    """
    Replaces all occurrences of double spaces with a single space in the input string.

    Args:
        input_string (str): The input string.

    Returns:
        str: The modified string with double spaces replaced by single spaces.
    """
    # return input_string.replace("  ", " ")
    return ' '.join(input_string.split())
    # Example usage:
    # example_string = "This  is  an  example  string  with  double      spaces."
    # result = replace_double_spaces(example_string)
    # print(result)  # Output: "This is an example string with double spaces."

def update_karaoke_db(directory_path):
    print("+update_karaoke_db")
    # Connect to the SQLite database
    db_path = "/Users/guyjasper/Library/Application Support/OpenKJ/OpenKJ/openkj.sqlite"  # Replace with the actual path to your database file
    
    # check if file exists
    if not os.path.isfile(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        #get all songs from DB with same folder 
        cursor.execute("SELECT path FROM dbsongs where path like ? order by path", (f"{directory_path}%",))    
        rows = cursor.fetchall()
        data_in_db = {normalize_path(row[0]): row[0] for row in rows}
        
        #get all files in folder        
        files_in_folder = get_files_in_directory(directory_path)
        
        #get new files in yet in DB
        new_files = find_new_files(data_in_db, files_in_folder)
        
        print(f"new files to add {len(new_files)}")
        for file in new_files:
            print(file)
        
        # Fetch all file paths
        # cursor.execute("SELECT DISTINCT path FROM sourceDirs")
        # rows = cursor.fetchall()

        # bFolderFound = False        
        # for row in rows:
        #     filepath = row[0]
            
        #     #get parent folder
        #     last_slash = filepath.rfind('/')
        #     if last_slash != -1:
        #         parent_folder = filepath[last_slash + 1:]
        #         print(parent_folder)
        #         if parent_folder == folder:
        #             bFolderFound = True
        #             break
        #         # parent_folders.add(parent_folder)
        
        # if bFolderFound == True:
        #     # query current entries
        #     cursor.execute("SELECT path FROM dbsongs where path like ? order by path", (f"{folder}%",))    
        #     rows = cursor.fetchall()
        #     print(len(rows))
        #     index = 0
        #     for row in rows:
        #         index = index + 1
        #         filepath = row[0]
        #         last_slash = filepath.rfind('/')
        #         if last_slash != -1:
        #             filename = filepath[last_slash+1:]
        #             print(f"[{index}] {filename}")
        
        print("All files processed.")
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        print("Database not updated.")
    finally:
        # Close the connection
        conn.close()
        print("-update_karaoke_db")
        
def get_files_in_directory(directory):
    filepaths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.startswith('.'):
                filepath = os.path.join(root, file)
                normalized = normalize_path(filepath)
                print(filepath,normalized)
                filepaths[f"\'{normalized}\'"] = filepath  # Map normalized to original
    return filepaths

def find_new_files(existing_files, directory_files):
    new_files = []
    for normalized, original in directory_files.items():
        if normalized not in existing_files:
            new_files.append(original)  # Add the original path
    return new_files

# Normalize paths for case-insensitive comparison
def normalize_path(path):
    path = os.path.abspath(path).replace("\\", "/")
    path = path.rstrip("/")
    return path.lower()

def convert_vp9_to_avc(input_file, output_file):
    """Converts a VP9 encoded video to AVC (H.264) with real-time logging."""
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_file
        ]
        # print(f"Starting conversion: {input_file} to {output_file}")
        print(f"Starting conversion: {os.path.basename(input_file)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) #using Popen instead of run.

        last_log = ""
        for line in process.stdout:
            if line.strip().startswith("frame="):
                if last_log != "":
                    print(f"\r{line.strip()}", end='')
                else:
                    last_log = line
                    print(f"ffmpeg: {line.strip()}", end='')  # log on the same line

        process.wait()  # wait for process to finish
        if process.returncode != 0:
            print(f"ffmpeg exited with non-zero code: {process.returncode}")
        else:
            print(f"\nConversion successful")
            print('Deleting original file...')
            os.remove(input_file)  # delete the original file
            os.rename(output_file, input_file)  # rename the new file to the original filename

    except FileNotFoundError:
        print("ffmpeg not found. Ensure it's installed and in your PATH.")
    except Exception as generic_error:
        print(f"A generic error has occurred: {generic_error}")

def get_video_codec_ffmpeg(filepath):
    try:
        probe = ffmpeg.probe(filepath)
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        
        if video_stream:
            return video_stream["codec_name"]
        else:
            return None
    except ffmpeg.Error as e:
        print(f"Error: {e.stderr.decode()}")
        return None

def check_video_codecs_in_directory(directory):
    """
    Checks the video codecs of all video files in the specified directory.

    Parameters:
        directory (str): The path to the directory containing the video files.

    Returns:
        dict: A dictionary with filenames as keys and their codecs as values.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"The provided path is not a directory: {directory}")

    for filename in os.listdir(directory):
        if filename.startswith('.'):
            continue
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            codec = get_video_codec_ffmpeg(full_path)
            if codec:
                print(f"File: {filename} - Video codec: {codec}")
            else:
                print(f"File: {filename} - Video codec not found or an error occurred")

def convert_all_vp9_to_mp4(directory, test_mode=False):
    """
    Converts all VP9 encoded videos in the specified directory to MP4 (H.264).

    Parameters:
        directory (str): The path to the directory containing the video files.
        bTest (bool): If True, only prints the files that need conversion without converting them.

    Returns:
        None: The function processes the files in place.
    """
    print("+convert_all_vp9_to_mp4", directory)
    if not os.path.isdir(directory):
        raise ValueError(f"The provided path is not a directory: {directory}")

    all_files = 0
    ctr = 0
    need_convert = 0
    invalid_codec = 0
    for root, _, files in os.walk(directory):
        ctr = 0
        print(f"\n\n**** Processing directory: {root} ****\n")
        for filename in sorted(files):
            if filename.startswith('.'):
                continue
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path) and os.path.splitext(full_path)[1].lower() in ['.mp4', '.mkv', '.webm', '.avi', '.mov']:
                ctr += 1
                all_files += 1
                codec = get_video_codec_ffmpeg(full_path)
                if codec:
                    if test_mode:
                        print(f"[{ctr}] {filename} - Video codec: {codec}")
                        if codec == "vp9" or codec == "av1":
                            need_convert += 1
                    else:
                        if codec == "vp9" or codec == "av1":
                            print(f"[{ctr}] {filename}")
                            output_file = os.path.splitext(full_path)[0] + "_2" + os.path.splitext(full_path)[1]
                            convert_vp9_to_avc(full_path, output_file)
                            print(f"File successfully converted to MP4\n")
                        else:
                            if codec == "h264":
                                print(f"[{ctr}] {filename} - Video codec: {codec} -- skipped")
                            else:
                                print(f"[{ctr}] {filename} - Video codec: {codec} -- skipped *************************")
                else:
                    print(f"[{ctr}] {filename} - Video codec not found or an error occurred")
                    invalid_codec += 1

    if test_mode:
        print(f"Total files: {all_files}")
        print(f"Files to convert: {need_convert}")
        print(f"Files with invalid codec: {invalid_codec}")

    print("All files processed.")

# Replace with the path to your directory
directory_path = "/Users/guyjasper/Desktop/Temp/KARAOKE FOR MEN"
    
if __name__ == "__main__":
    # directory_path = "/Users/guyjasper/Desktop/Don & Irish/JPG_8X12" 
    # update_karaoke_db(directory_path)
    
    # check_video_codecs_in_directory(directory_path)
    convert_all_vp9_to_mp4(directory_path, True)
    
    # filepath = '/Volumes/KINGSTONSSD/_Karaoke/BEST OF 90s/Goo Goo Dolls - Iris.mp4'
    # print(f"File: {filepath}")
    # codec = get_video_codec_ffmpeg(filepath)
    # if codec:
    #     print(f"Video codec: {codec}")
    #     if codec == 'vp9':
    #         print("Converting to AVC")            
    #         output_file = filepath.replace(".mp4", "_2.mp4")
    #         convert_vp9_to_avc(filepath, output_file)
    #         print(f"File: {output_file}")
    #         codec = get_video_codec_ffmpeg(output_file)
    #         if codec:
    #             print(f"Video codec: {codec}")
    #         else:   
    #             print("Video codec not found or an error occurred")
    # else:   
    #     print("Video codec not found or an error occurred")
            
    
    # files = get_files_in_directory(directory_path)
    # index=0
    # for file in files:
    #     index = index + 1
    #     print(f"[{index}] {file}")
    
    # remove_duplicate_in_directory(directory_path)
    # fix_filenames_in_directory("/Users/guyjasper/Documents/Guy/Projects/Python/DownloadYT/NEW_SONGS")
    # temp = remove_keywords("Ilysb (stripped) - Male Key - Full Band Karaoke - Instrumental -  Lany.mp4")
    # print(to_title_case(replace_double_spaces(temp)))

