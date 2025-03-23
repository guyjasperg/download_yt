#!/usr/bin/env python3

import os
import re
import sqlite3
# import ffmpeg
import subprocess
import logging
import shutil
import argparse
import sys, threading
import json
import requests

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
    "Instrumental"
    ]

def remove_keywords(filename, keywords=None):
    global keywords_to_remove
    
    if keywords is None:
        keywords = []

    name, ext = os.path.splitext(filename)
    new_name = name.strip()
    keywordtoremove = keywords_to_remove if keywords == [] else keywords

    # clean invalid characters first
    invalid_chars = ['(', ')', '[', ']','{','}', '*', '_', '|', '/','+', '🎤', '🎵','♫','♪']
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
    # Ensure new_name does not end with '-', '.', or '_'
    while new_name and new_name[-1] in '-._':
        new_name = new_name[:-1]
    
    # Remove double spaces
    while '  ' in new_name:
        new_name = new_name.replace('  ', ' ')        
    
    # Strip white spaces from the name and extension
    new_name = new_name.strip()
    
    new_name = f"{new_name}{ext}"
    print(new_name)
    return new_name

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

def update_karaoke_db(directory_path, db_path,message_callback=None, upload_to_server=False, server_url=""):
    print("+update_karaoke_db")
    if message_callback:
        message_callback("Updating karaoke database...")
    # Connect to the SQLite database
    # db_path = "/Users/guyjasper/Library/Application Support/OpenKJ/OpenKJ/openkj.sqlite"  # Replace with the actual path to your database file
    
    # check if file exists
    if not os.path.isfile(db_path):
        print(f"Database file not found: {db_path}")
        if message_callback:
            message_callback(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        #get all songs from DB with same folder 
        cursor.execute("SELECT path FROM dbsongs where path like ? order by path", (f"{directory_path}%",))    
        rows = cursor.fetchall()
        data_in_db = sorted([row[0] for row in rows])
        
        # log the data
        # print('Data in database')
        # for file in data_in_db:
        #     print(file)
        # data_in_db = {normalize_path(row[0]): row[0] for row in rows}
        
        #get all files in folder        
        files_in_folder = get_files_in_directory(directory_path)
        
        #get new files in yet in DB
        new_files = find_new_files(data_in_db, files_in_folder)
        
        # Initialize the list to store songs to add
        songs_to_add = []
        
        print(f"new files to add {len(new_files)}")
        if message_callback:
            message_callback(f"new files to add {len(new_files)}")
            
        for file in new_files:
            filename = os.path.basename(file)
            if filename.count('-') == 1:
                filename_no_ext = os.path.splitext(filename)[0]
                title, artist = filename_no_ext.rsplit('-', 1)
                artist = artist.strip()
                title = title.strip()
                
                # Get the duration of the video file
                duration = get_video_duration(file)
                print(f'Artist: {artist}, Title: {title}',duration)
                if message_callback:
                    message_callback(f'Artist: {artist}, Title: {title}, Duration: {duration}')
                # Save artist, title, filepath, and duration to a list for later batch saving to database
                songs_to_add.append((artist, title, file, duration))
            else:
                print(f"\nFilename does not contain exactly one '-': {filename}")
                if message_callback:
                    message_callback(f"\nFilename does not contain exactly one '-': {filename}")
                artist = input("\nEnter Artist name: ").strip()
                title = input("Enter Title: ").strip()
                
                if artist and title:
                    duration = get_video_duration(file)
                    print(f'Artist: {artist}, Title: {title}',duration)
                    # Save artist, title, filepath, and duration to a list for later batch saving to database
                    songs_to_add.append((artist, title, file, duration))
                else:
                    print("skipping file...")
                    if message_callback:
                        message_callback("skipping file...")
                
        if songs_to_add:
            print('saving to database...')
            if message_callback:
                message_callback("saving to database...")
            try:
                # Begin a transaction
                conn.execute("BEGIN TRANSACTION;")
                
                # Insert songs into the database
                cursor.executemany("INSERT INTO dbsongs (artist, title, path, duration) VALUES (?, ?, ?, ?);", songs_to_add)
                
                # Commit the transaction
                conn.commit()
                conn.close()
                print(f"Inserted {len(songs_to_add)} new songs into the database.")
                if message_callback:
                    message_callback(f"Inserted {len(songs_to_add)} new songs into the database.")
                
                if upload_to_server and server_url!="":
                    print("Uploading database to server...")
                    if message_callback:
                        message_callback("Uploading database to server...")
                    upload_karaoke_db(db_path, server_url)
                
            except sqlite3.Error as e:
                # Rollback the transaction in case of error
                conn.rollback()
                print(f"An error occurred while inserting songs: {e}")
                if message_callback:
                    message_callback(f"An error occurred while inserting songs: {e}")
        print("All files processed.")
        if message_callback:
            message_callback("All files processed.")
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if message_callback:
            message_callback(f"An error occurred: {e}")
        print("Database not updated.")
        if message_callback:
            message_callback("Database not updated.")
    finally:
        # Close the connection
        if conn:
            conn.close()
        print("-update_karaoke_db")
        if message_callback:
            message_callback("-update_karaoke_db")

def upload_karaoke_db(dbFile, server_url):
    """Uploads a file to a Node.js Express server."""
    try:
        with open(dbFile, 'rb') as file:
            files = {'dbFile': (file.name, file, 'application/octet-stream')} #application/octet-stream is a safe default.
            response = requests.post(server_url, files=files)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
    except FileNotFoundError:
        print(f"File not found: {dbFile}")    

def get_files_in_directory(directory):
    filepaths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.startswith('.'):
                filepath = os.path.join(root, file)
                filepaths.append(filepath)
    
    filepaths = sorted(filepaths)
    # print('Files in directory')
    # for file in filepaths:
    #     print(file)
    return filepaths

def find_new_files(existing_files, directory_files):
    new_files = []
    for file in directory_files:
        if file not in existing_files:
            new_files.append(file)  # Add the original path
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
            if input_file.lower().endswith(".mkv"):
                input_file = os.path.splitext(input_file)[0] + ".mp4"
            os.rename(output_file, input_file)  # rename the new file to the original filename

    except FileNotFoundError:
        print("ffmpeg not found. Ensure it's installed and in your PATH.")
    except Exception as generic_error:
        print(f"A generic error has occurred: {generic_error}")

def get_video_duration(video_path):
    try:
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path,
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        probe = json.loads(result.stdout)
        
        duration_seconds = float(probe['format']['duration'])
        return int(duration_seconds * 1000)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing ffprobe output: {e}")
        return None    

def get_video_codec_ffmpeg(filepath):
    try:
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filepath,
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        probe = json.loads(result.stdout)
        
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        if video_stream:
            return video_stream['codec_name']
        else:
            return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing ffprobe output: {e}")
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
                        if codec == "vp9" or codec == "av1" or os.path.splitext(full_path)[1].lower() == ".mkv":
                            need_convert += 1
                            
                            if copy_files:
                                sub_dir = os.path.join(root, os.path.basename(root.rstrip('/')))
                                print(sub_dir)
                                if not os.path.exists(sub_dir):
                                    os.makedirs(sub_dir)
                                print(f"copying file to [{sub_dir}]")
                                shutil.copy(full_path, sub_dir)
                                # copy file to sub directory
                                                                                    
                        if codec != "h264":
                            invalid_codec += 1
                    else:
                        if codec == "vp9" or codec == "av1" or os.path.splitext(full_path)[1].lower() == ".mkv":
                            print(f"[{file_num}] {filename}")
                            if os.path.splitext(full_path)[1].lower() == ".mkv":
                                output_file = os.path.splitext(full_path)[0] + "_2.mp4"
                            else:
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

def get_all_none_mp4(directory):
    """
    Converts all VP9 encoded videos in the specified directory to MP4 (H.264).

    Parameters:
        directory (str): The path to the directory containing the video files.
        bTest (bool): If True, only prints the files that need conversion without converting them.

    Returns:
        None: The function processes the files in place.
    """
    print("+get_all_none_mp4", directory)
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
        # file_count = count_video_files(root)
        for filename in sorted(files):
            if filename.startswith('.'):
                continue
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path) and os.path.splitext(full_path)[1].lower() in ['.mkv', '.webm', '.avi', '.mov']:
                ctr += 1
                file_num = f'{ctr}'
                print(f"[{file_num}] {filename}")
                
    print("All files processed.")

def download_karaoke_db(db_path, server_url, message_callback=None):
    """
    Downloads the karaoke database file from the server.
    
    Args:
        db_path (str): Local path where to save the database file
        server_url (str): URL of the server's download endpoint
        message_callback (function): Optional callback function to handle status messages
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Send GET request to download the file
        response = requests.get(server_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a backup of the existing database if it exists
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup"
            shutil.copy2(db_path, backup_path)
            if message_callback:
                message_callback(f"Created backup at: {backup_path}")
        
        # Save the downloaded file
        with open(db_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if message_callback:
            message_callback(f"Database downloaded successfully to: {db_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error downloading database: {str(e)}"
        if message_callback:
            message_callback(error_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if message_callback:
            message_callback(error_msg)
        return False

def delete_song_from_db(db_path, song_id, song_filepath):
    """Delete a song from the database by its ID and remove the associated file.
    
    Args:
        db_path (str): Path to the SQLite database file
        song_id (int): ID of the song to delete
        song_filepath (str): Path to the song file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
        
    Raises:
        sqlite3.Error: If there's a database error
        OSError: If there's an error deleting the file
    """
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete from database
        delete_query = "DELETE FROM dbsongs WHERE songid = ?"
        cursor.execute(delete_query, (song_id,))
        conn.commit()
        
        # Delete the actual file if it exists
        if os.path.exists(song_filepath):
            os.remove(song_filepath)
            print(f"Deleted file: {song_filepath}")
        else:
            print(f"File not found: {song_filepath}")
        
        return True
        
    except sqlite3.Error as e:
        raise e
    except OSError as e:
        # If file deletion fails, rollback database changes
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# Replace with the path to your directory
directory_path = "/Volumes/KINGSTONSSD/_Karaoke/_NEW_SONGS"
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility functions for processing files.")
    # parser.add_argument("--directory", type=str, required=True, help="Path to the directory to process.")
    # parser.add_argument("--update_db", action="store_true", help="Update the karaoke database.")
    parser.add_argument("--check_codecs", action="store_true", help="Check video codecs in the directory.")
    parser.add_argument("--convert_vp9", action="store_true", help="Convert VP9 videos to MP4 (H.264).")
    parser.add_argument("--test_mode", action="store_true", help="Run in test mode (no actual conversion).")
    parser.add_argument("--copy_files", action="store_true", help="Copy files to subdirectory before conversion.")
    parser.add_argument("--remove_duplicates", action="store_true", help="Remove duplicate files in the directory.")
    parser.add_argument("--fix_filenames", action="store_true", help="Fix filenames in the directory.")
    parser.add_argument("--get_none_mp4", action="store_true", help="Get all other video files.")
    parser.add_argument("--play_sound", action="store_true", help="Play mp3 file.")
    parser.add_argument("--clean_filename", action="store_true", help="Remove keywords in filename")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Subparser for the get_files_in_directory command
    parser_vid = subparsers.add_parser("vid_utils", help="ffmpeg utilities")
    parser_vid.add_argument("--directory", required=True, help="The directory to list video files from.")
    parser_vid.add_argument("--database", required=True, help="Sqlite database")
    parser_vid.add_argument("--test_mode", action="store_true")
    parser_vid.add_argument("--upload", action="store_true", help="Uploads database to server after updating")
    parser_vid.add_argument("--server_url", required='--upload' in sys.argv, help="Server URL where to upload database")

    args = parser.parse_args()
    
    if args.command == "vid_utils":
        print("Manage karaoke video files...", args.directory, args.database)
        update_karaoke_db(args.directory, args.database,None, args.upload, args.server_url)
    else:        
        match args:
            case _ if args.check_codecs:
                check_video_codecs_in_directory(args.directory)
            case _ if args.convert_vp9:
                print('convert_vp9', args.directory, args.test_mode, args.copy_files)
                convert_all_vp9_to_mp4(args.directory, args.test_mode, args.copy_files)
            case _ if args.remove_duplicates:
                remove_duplicate_in_directory(args.directory)
            case _ if args.fix_filenames:
                fix_filenames_in_directory(args.directory)
            case _ if args.get_none_mp4:
                get_all_none_mp4(args.directory)
            case _ if args.clean_filename:
                remove_keywords('Splender Yeah, Whatever + Instrumental.mp4')

