import os
import re
import sqlite3
import ffmpeg
import subprocess
import logging
import shutil
import argparse
import sys, threading

SOUND_NOTIF = './Sounds/arpeggio-467.mp3'
SOUND_ERROR = './Sounds/glitch-notification.mp3'
SOUND_PROCESS_COMPLETE = './Sounds/hitech-logo.mp3'

# Function to play sound in a separate thread
def play_sound(file_path):
    threading.Thread(target=play_sound_threaded, args=(file_path,), daemon=True).start()

def play_sound_threaded(file_path):
    if not os.path.exists(file_path):
        print(f"play_sound Error: File '{file_path}' not found.")
        return

    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["aplay", file_path], check=True)
        else:
            print("play_sound: Unsupported operating system.")
    except Exception as e:
        print(f"Error playing sound: {e}")    

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
    "lower key",
    "with lyrics",
    "studio version",
    "version in the style of",
    "in the style of ",
    "piano version",
    "acoustic instrumental",
    ]

def remove_keywords(filename, keywords=None):
    global keywords_to_remove
    
    if keywords is None:
        keywords = []

    new_name = filename
    keywordtoremove = keywords_to_remove if keywords == [] else keywords

    # clean invalid characters first
    invalid_chars = ['(', ')', '[', ']', '*', '_', '|', '🎤', '🎵']
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

# Normalize paths for case-insensitive comparison
def normalize_path(path):
    path = os.path.abspath(path).replace("\\", "/")
    path = path.rstrip("/")
    return path.lower()

def convert_vp9_to_avc(input_file, output_file):
    """Converts a VP9 encoded video to AVC (H.264) with real-time logging."""
    try:
        # Delete output file if it exists
        if os.path.isfile(output_file):
            os.remove(output_file)
            print(f"Deleted existing output file: {output_file}")

        command = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_file
        ]
        # print(f"Starting conversion: {input_file} to {output_file}")
        print(f"Starting conversion: {os.path.basename(input_file)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) #using Popen instead of run.

        last_log = None
        for line in process.stdout:
            if line.strip().startswith("frame="):
                if last_log != None:
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

def get_video_duration(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        duration_seconds = float(probe['format']['duration'])
        return duration_seconds
    except Exception as e:
        print(f"Error probing video: {e}")
        return None

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

def convert_all_vp9_to_mp4(directory, test_mode=False, copy_files = False):
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
        print(f"!!!!!! The provided path is not a directory: {directory}")
        return

    all_files = 0
    ctr = 0
    need_convert = 0
    invalid_codec = 0
    for root, _, files in os.walk(directory):
        ctr = 0
        print(f"\n\n**** Processing directory: {root} ****\n")
        file_count = count_video_files(root)
        for filename in sorted(files):
            if filename.startswith('.'):
                continue
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path) and os.path.splitext(full_path)[1].lower() in ['.mp4', '.mkv', '.webm', '.avi', '.mov']:
                ctr += 1
                file_num = f'{ctr} of {file_count}'
                all_files += 1
                codec = get_video_codec_ffmpeg(full_path)                
                if codec:
                    if test_mode:
                        print(f"[{file_num}] {filename} - Video codec: {codec}")
                        if codec == "vp9" or codec == "av1":
                            need_convert += 1
                            
                            if copy_files:
                                sub_dir = os.path.join(root, os.path.basename(root))
                                if not os.path.exists(sub_dir):
                                    os.makedirs(sub_dir)
                                print(f"copying file to [{sub_dir}]")
                                shutil.copy(full_path, sub_dir)
                                # copy file to sub directory
                                                                                    
                        if codec != "h264":
                            invalid_codec += 1
                    else:
                        if codec == "vp9" or codec == "av1":
                            print(f"[{file_num}] {filename}")
                            output_file = os.path.splitext(full_path)[0] + "_2" + os.path.splitext(full_path)[1]
                            convert_vp9_to_avc(full_path, output_file)
                            print(f"File successfully converted to MP4\n")
                        else:
                            if codec == "h264":
                                print(f"[{file_num}] {filename} - Video codec: {codec} -- skipped")
                            else:
                                print(f"[{file_num}] {filename} - Video codec: {codec} -- skipped *************************")
                else:
                    print(f"[{file_num}] {filename} - Video codec not found or an error occurred")
                    invalid_codec += 1

    if test_mode:
        print(f"Total files: {all_files}")
        print(f"Files to convert: {need_convert}")
        print(f"Files with invalid codec: {invalid_codec}")

    print("All files processed.")

# Replace with the path to your directory
directory_path = "/Volumes/KINGSTONSSD/_Karaoke/_NEW_SONGS"
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility functions for processing files.")
    parser.add_argument("--directory", type=str, required=True, help="Path to the directory to process.")
    parser.add_argument("--update_db", action="store_true", help="Update the karaoke database.")
    parser.add_argument("--check_codecs", action="store_true", help="Check video codecs in the directory.")
    parser.add_argument("--convert_vp9", action="store_true", help="Convert VP9 videos to MP4 (H.264).")
    parser.add_argument("--test_mode", action="store_true", help="Run in test mode (no actual conversion).")
    parser.add_argument("--copy_files", action="store_true", help="Copy files to subdirectory before conversion.")
    parser.add_argument("--remove_duplicates", action="store_true", help="Remove duplicate files in the directory.")
    parser.add_argument("--fix_filenames", action="store_true", help="Fix filenames in the directory.")
    
    parser.add_argument("--play_sound", action="store_true", help="Play mp3 file.")

    args = parser.parse_args()

    if args.update_db:
        update_karaoke_db(args.directory)
    
    if args.check_codecs:
        check_video_codecs_in_directory(args.directory)
    
    if args.convert_vp9:
        print('convert_vp9', args.directory, args.test_mode, args.copy_files)
        convert_all_vp9_to_mp4(args.directory, args.test_mode, args.copy_files)
    
    if args.remove_duplicates:
        remove_duplicate_in_directory(args.directory)
    
    if args.fix_filenames:
        fix_filenames_in_directory(args.directory)

