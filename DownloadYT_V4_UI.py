
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog  # For folder selection dialog

from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import os
import time
import subprocess
from UtilityFunctions import *

basse_url = 'https://www.youtube.com/watch?v='
video_id = 'HNy41EFCJcs'

RAW_FOLDER = "DOWNLOADS/"
MERGED_FOLDER = "NEW_SONGS/"

video_filename = ""
audio_filename = ""

yt = None

def on_progress(stream, chunk, bytes_remaining):
  """
  Callback function to display download progress.

  Args:
    stream: The stream being downloaded.
    chunk: The size of the downloaded chunk.
    bytes_remaining: The number of bytes remaining to be downloaded.
  """
  total_size = stream.filesize
  bytes_downloaded = total_size - bytes_remaining
  percentage_of_completion = bytes_downloaded / total_size * 100
  
  progress = f"Downloaded: {bytes_downloaded / 1024 / 1024:.2f}MB / {total_size / 1024 / 1024:.2f}MB ({percentage_of_completion:.2f}%)"
  
  # get last line in the progress logs
  last_line = get_last_line()
  if last_line.startswith('Downloaded:'):
    update_last_line(progress)
  else:
      insertLog(progress)

def start_download():
    insertLog(f'Start download\n{url_entry.get()}')

def insertLog(log):
    txtLogs.configure(state=tk.NORMAL)
    txtLogs.insert(tk.END,f"{log}\n")
    txtLogs.see(tk.END) # Auto-scroll to the bottom
    txtLogs.configure(state=tk.DISABLED)
    
def clearLogs():
    txtLogs.delete("1.0", tk.END)
    
# Function to get the last line text
def get_last_line():
    # Temporarily enable the widget for reading
    txtLogs.config(state=tk.NORMAL)
    
    # Get the index of the start of the last line
    last_line_start = txtLogs.index("end-2c linestart")  # Start of the last line
    
    # Get the text of the last line
    last_line_text = txtLogs.get(last_line_start, "end-1c")  # End of the last line
    
    # Disable the widget again
    txtLogs.config(state=tk.DISABLED)
    
    return last_line_text.strip()  # Strip any trailing whitespace/newline

# Function to update the last line with progress
def update_last_line(progress):
    # Temporarily enable the widget for editing
    txtLogs.config(state=tk.NORMAL)
    
    # Get the index of the last line
    last_line_index = txtLogs.index("end-2c linestart")  # Start of the last line
    
    # Delete the last line
    txtLogs.delete(last_line_index, tk.END)
    
    # Insert the updated progress
    txtLogs.insert(tk.END, f"Progress: {progress}%\n")
    txtLogs.see(tk.END)  # Auto-scroll to the bottom
    
    # Disable the widget again
    txtLogs.config(state=tk.DISABLED)    

# Init
# Make sure temp folders exists
if not os.path.isdir(RAW_FOLDER):
    os.mkdir(RAW_FOLDER)
    
if not os.path.isdir(MERGED_FOLDER):
    os.mkdir(MERGED_FOLDER)

# **********************************
# Create the main application window
# **********************************
root = tk.Tk()
root.title("YouTube Video Downloader")
# root.geometry("700x400")
root.configure(bg="#FFFFFF")

frame = tk.Frame()

# Label and Entry for the YouTube URL
url_label = tk.Label(frame, text="YouTube URL:")
url_label.grid(row=0, column=0, padx=2, pady=5)

url_entry = tk.Entry(frame, width=50)
url_entry.grid(row=0, column=1, padx=2, pady=5)

# Button to start the download
download_button = tk.Button(frame, text="Download", command=start_download)
download_button.grid(row=0, column=2, padx=2, pady=5)

# Multiline Textbox for progress updates

txtLogs = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
txtLogs.grid(row=1, column=0, columnspan=3, pady=5)
txtLogs.configure(state=tk.DISABLED)

btn_clear_logs = tk.Button(frame, text="Clear Logs", command=clearLogs)
btn_clear_logs.grid(row=2, column=1, pady=5)

frame.pack()

# Run the application
root.mainloop()