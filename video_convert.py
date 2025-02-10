import sqlite3
import subprocess
import os, sys

def update_db_for_avi(db_file):
  """
  Updates the 'dbsongs' table in the given SQLite database 
  to only include rows where the last 4 characters of the 'path' field are '.avi'.

  Args:
    db_file: Path to the SQLite database file.
  """
  try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # SQL query to delete rows where the last 4 characters of 'path' are not '.avi'
    # sql = """
    #   SELECT * FROM dbsongs
    #   WHERE substr(path, -4) == '.avi';
    # """
    sql = """
      UPDATE dbsongs
      SET path = REPLACE(path, '.avi', '.mp4')
      WHERE substr(path, -4) = '.avi';
    """
    cursor.execute(sql)

    conn.commit()
    print("Database updated successfully.")

  except sqlite3.Error as e:
    print(f"An error occurred: {e}")

  finally:
    if conn:
      conn.close()

def find_avi_files(root_dir):
  """
  Finds all AVI files within a given directory and its subdirectories, excluding hidden files.

  Args:
    root_dir: The root directory to start the search from.

  Returns:
    A list of full paths to all AVI files found.
  """
  avi_files = []
  for root, dirs, files in os.walk(root_dir):
    # Exclude hidden directories
    dirs[:] = [d for d in dirs if not d.startswith('.')] 
    for file in files:
      if not file.startswith('.') and file.endswith(".avi"):
        avi_files.append(os.path.join(root, file))
  return avi_files

def ffmpeg_callback(line):
  """
  Callback function to process FFmpeg output lines and print progress on the same line.

  Args:
    line: A single line of output from the FFmpeg process.
  """
  if "frame=" in line:
    # Extract relevant information (adjust based on FFmpeg output format)
    try:
    #   frame_str, _, time_str, _ = line.split("=", 3) 
    #   frame_num = int(frame_str.split(" ")[1])
    #   time_str = time_str.split(" ")[0] 
      
      # Print progress to the same line
    #   print(f"\rProcessing: {time_str} / {frame_num} frames", end="")
      print(f"\rProcessing: {line.strip()}", end="")
      sys.stdout.flush()  # Ensure immediate output
    except ValueError:
      pass  # Ignore lines that cannot be parsed  # Print the progress line to the console
#   else:
#       print(line)

def convert_avi_to_mp4(input_file):
  """
  Converts an AVI video file to MP4 format using FFmpeg and deletes the original AVI file.

  Args:
    input_file: Path to the input AVI file.
  """
  try:
    # Extract filename without extension
    filename, _ = os.path.splitext(input_file) 
    output_file = filename + '.mp4'
    
    print('+convert_avi_to_mp4', filename)

    command = [
        'ffmpeg', 
        '-i', input_file, 
        '-loglevel', 'info',
        '-c:v', 'libx264', 
        '-c:a', 'aac', 
        output_file
    ]
    
    print("converting video...")
        # Use subprocess.Popen with stdout=subprocess.PIPE to capture output
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
      for line in proc.stdout:
        ffmpeg_callback(line)  # Call the callback function for each line

      proc.wait() 
      print("\n...")
      if proc.returncode == 0:
        print(f"Successfully converted {input_file} to {output_file}")
        os.remove(input_file)
        print(f"Deleted original AVI file: {input_file}")
      else:
        raise subprocess.CalledProcessError(proc.returncode, command)
    
    # subprocess.run(command, check=True)
    # print(f"Successfully converted {input_file} to {output_file}")

    # Delete the original AVI file
    # os.remove(input_file)
    # print(f"Deleted original AVI file: {input_file}")
    print('-convert_avi_to_mp4')
  except subprocess.CalledProcessError as e:
    print(f"Error converting {input_file}: {e}")

# Example usage:
folder_path = '/Volumes/KINGSTONSSD/_Karaoke'
avi_file_paths = find_avi_files(folder_path)

avi_count = len(avi_file_paths)
print(avi_count)
ctr = 1
for file_path in avi_file_paths:
  print(f"\n{ctr} of {avi_count}")
  convert_avi_to_mp4(file_path)
  ctr = ctr + 1 

# print(len(avi_file_paths))

# input_avi= "/Volumes/KINGSTONSSD/_Karaoke/2024 KARAOKE/Alaala - Freddie Aguilar.avi"
# convert_avi_to_mp4(input_avi)

# db_path = "/Users/guyjasper/Library/Application Support/OpenKJ/OpenKJ/openkj.sqlite"  # Replace with the actual path to your database file
# update_db_for_avi(db_path)