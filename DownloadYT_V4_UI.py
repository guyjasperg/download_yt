#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog  # For folder selection dialog

from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from UtilityFunctions import *
import os, subprocess, threading, queue
import json  # For parsing JSON

RAW_FOLDER = "DOWNLOADS/"
MERGED_FOLDER = "NEW_SONGS/"

SOUND_NOTIF = 'arpearpeggio-467.mp3'

# need to use youtube-po-token-generator to generate poToken and visitorData
js_url =  './youtube-po-token-generator/examples/one-shot.js'
VISITOR_DATA = 'CgtKbVR3aVJQUTUxcyic5fy8BjIKCgJQSBIEGgAgbg%3D%3D'
PO_TOKEN = 'MnRH5JFMhu5OqUfcnrah0Bf_GmXlDOP08QPu9RFMLSJtZQRocmea4VGzTCEgMfoGXur3S_IdichbZKmYiEUtWqG5wY4dj29DAypotNrsSry0NvUr8Zk16KWsr1ulG2oXvCRJ_8JsERbT3FzT2DaT1ONpPvVopA=='

def get_po_token_thread():
    message_queue.put('+get_po_token')
    
    message_queue.put('+subprocess')
    result = subprocess.run(
            ["node", js_url],  # Ensure Node.js is installed and accessible
            capture_output=True,
            text=True
        )
    message_queue.put('-subprocess')
    if result.returncode != 0:
        message_queue.put(f"Error running JavaScript: {result.stderr}")
    else:
        data = result.stdout.strip()
        # message_queue.put(f'data: {data}')

        result_data = json.loads(data)  # Parse the JSON output

        visitorData = result_data.get("visitorData")
        if visitorData:
            message_queue.put(f'visitorData: {visitorData}')
            VISITOR_DATA = visitorData
        else:
            message_queue.put('visitorData not found!')
            
        po_token = result_data.get("poToken")  # Get the poToken value
        if po_token:
            message_queue.put(f'poToken: {po_token}')
            PO_TOKEN = po_token
        else:
            message_queue.put('poToken not found!')

    message_queue.put('-get_po_token()')
    is_downloading = False    

def get_po_token():
    # Set the downloading flag
    global is_downloading
    
    is_downloading = True
    
    # Run the download in a separate thread
    threading.Thread(target=get_po_token_thread, daemon=True).start()
            
    # Start processing the queue
    process_queue()


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
  
  print(progress)
  message_queue.put(progress)
  
  # get last line in the progress logs

def Downloadfiles(videostream, audiostream):
    global video_filename
    global audio_filename
    global yt

    message_queue.put(f"Downloadfiles({videostream.title})\n")

    try:        
        if videostream:
            #title = CleanFilename(videostream.default_filename)
            message_queue.put(f"[{video_filename}]\n")
            ys = yt.streams.get_by_itag(videostream.itag)
            ys.download(filename=f"{RAW_FOLDER}{video_filename}")

        if audiostream:
            #title = audiostream.default_filename
            message_queue.put(f"\n[{audio_filename}]\n")
            ys = yt.streams.get_by_itag(audiostream.itag)
            ys.download(filename=f"{RAW_FOLDER}{audio_filename}")

        return True
    except Exception as e:
        message_queue.put(f"ERROR: An error occurred downloading files. [{e}]")
        return False
    
# Queue for thread-safe communication
message_queue = queue.Queue()

# Flag to track if a download is in progress
is_downloading = False

# Periodically check the queue and update the UI
# Periodically check the queue and update the UI
def process_queue():
    try:
        while not message_queue.empty():
            message = message_queue.get_nowait()  # Get a message from the queue
            insertLog(message)
            
            # if message.startswith('Downloaded:'):
            #     last_line = get_last_line()
            #     if last_line.startswith('Downloaded:'):
            #         update_last_line(message)
            #     else:
            #         insertLog(message)
            # else:
            #     insertLog(message)
            
            # enable button if done
            if message == '-thread_download_video' or message == '-get_po_token()':
                download_button.config(state=tk.NORMAL)
                if message == '-get_po_token()':
                    txt_poToken.delete(0, tk.END)
                    txt_poToken.insert(tk.END, PO_TOKEN)
                    txt_visitor.delete(0, tk.END)
                    txt_visitor.insert(tk.END, VISITOR_DATA)
                    
    except queue.Empty:
        pass

    # Continue processing the queue only if a download is in progress
    if is_downloading:
        root.after(50, process_queue)  # Check the queue again after 100ms
        
def start_download_thread(url):
    global video_filename
    global audio_filename
    global yt
    global is_downloading
    global PO_TOKEN, VISITOR_DATA
    
    try:
        try:
            message_queue.put("contacting server...\n")
            
            # modified YouTube class to use po_token paramater            
            yt = YouTube(url,'WEB', po_token=PO_TOKEN, visitor_data=VISITOR_DATA, on_progress_callback=on_progress )
        except Exception as e:
            message_queue.put(f"ERROR: An error occurred: {e}")
            return
        
        # continue
        message_queue.put(f'YT Title: {yt.title}')
        
        #select highest resolution video
        # Sort streams by resolution in descending order
        selectedVideoStream = None
        sorted_streams = sorted(yt.streams.filter(type="video"), key=lambda s: s.resolution) 

        for stream in sorted_streams:
            if(stream.height >= 360 and stream.subtype == "mp4"):
                if(selectedVideoStream == None):
                    selectedVideoStream = stream
                    if stream.height == 1080:
                        break
                else:
                    if(selectedVideoStream.height < stream.height):
                        selectedVideoStream = stream
                        if stream.height == 1080:
                            break
        
        if selectedVideoStream != None:
            video_filename = f"{remove_keywords(CleanFilename(selectedVideoStream.default_filename),"")}"
            message_queue.put(f"selected video stream: [{selectedVideoStream.itag}] {selectedVideoStream.resolution}")
            if selectedVideoStream.includes_audio_track == False:
                message_queue.put("No audio track")
        else:
            message_queue.put("No video stream selected.")
            
        # getting audio track
        #if stream has no audio, select audio stream
        selectedAudioStream = None
        if selectedVideoStream.includes_audio_track == False:
            message_queue.put("searching audio track")
            #select audio
            for stream1 in yt.streams.filter(type="audio"):
                #filter only for mp4
                if(stream1.abr == '128kbps'):
                    selectedAudioStream = stream1            

        audio_filename = ""
        if selectedAudioStream != None:
            #print(selectedAudioStream.default_filename)
            audio_filename = f"{remove_keywords(CleanFilename(selectedAudioStream.default_filename),"")}"
            message_queue.put(f"selected audio stream: [{selectedAudioStream.itag}] {selectedAudioStream.abr}\n")
        else:
            message_queue.put("No audio stream selected")

        # message_queue.put("\nDownloading files...")       
        if Downloadfiles(selectedVideoStream, selectedAudioStream) == False:
            message_queue.put('Download failed.')
            return
        
        # successful download, proceed processing
        # Merge video and audio files
        if selectedAudioStream != None:
            message_queue.put("\nMerging audio and video streams...")

            # Combine video and audio using ffmpegexit            
            output_file = f"{MERGED_FOLDER}{video_filename}"
            message_queue.put(f"saving file to ->{output_file}")

            if os.path.isfile(output_file):
                message_queue.put("File already exists!")
                return
            
            command = [
                'ffmpeg',
                '-i', f"{RAW_FOLDER}{video_filename}",
                '-i', f"{RAW_FOLDER}{audio_filename}",
                '-loglevel', 'warning',
                '-c:v', 'copy',  # Copy video codec (no re-encoding)
                '-c:a', 'aac',   # Use AAC codec for audio
                '-strict', 'experimental',  # To ensure ffmpeg accepts the audio format
                output_file
            ]
            subprocess.run(command, check=True)

            # If successful, delete the original video and audio files (optional)
            os.remove(f"{RAW_FOLDER}{video_filename}")
            os.remove(f"{RAW_FOLDER}{audio_filename}")            
            message_queue.put('Video successfully downloaded.')            
    except Exception as e:
        message_queue.put(f"Error: {str(e)}")
    finally:
        # Reset the downloading flag
        message_queue.put('-thread_download_video')
        is_downloading = False        

def start_download():
    global is_downloading
        
    # check if there is valid input
    url = txturl.get()
    if url:
        clearLogs()
        
        insertLog(f'YT url: {url}')
        
        # Set the downloading flag
        is_downloading = True
        
        # Run the download in a separate thread
        threading.Thread(target=start_download_thread, args=(url,), daemon=True).start()
                
        # Start processing the queue
        process_queue()

        # disable button to prevent disrupting current process
        download_button.config(state=tk.DISABLED)
    else:
        insertLog('Please enter YT url to download.')        
    
def insertLog(log):
    txtLogs.configure(state=tk.NORMAL)  # Enable editing

    # Get the current content of the ScrolledText widget
    current_content = txtLogs.get("1.0", tk.END).strip()  # Strip trailing newline

    if log.startswith("Downloaded:"):
        # Split the content into lines
        lines = current_content.split("\n")

        # Check if the last line starts with "Downloaded:"
        if lines and lines[-1].startswith("Downloaded:"):
            # Replace the last line with the new log
            lines[-1] = log
        else:
            # Append the new log as a new line
            lines.append(log)        
        
        # Clear the widget and re-insert all lines
        txtLogs.delete("1.0", tk.END)
        txtLogs.insert(tk.END, "\n".join(lines) + "\n")        
    else:
        txtLogs.insert(tk.END,f"{log}\n")

    # Auto-scroll to the bottom
    txtLogs.see(tk.END)

    # Disable editing
    txtLogs.configure(state=tk.DISABLED)
        
def clearLogs():
    txtLogs.configure(state=tk.NORMAL)
    txtLogs.delete("1.0", tk.END)
    txtLogs.configure(state=tk.DISABLED)
    
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
    txtLogs.insert(tk.END, f"{progress}%")
    txtLogs.see(tk.END)  # Auto-scroll to the bottom
    
    # Disable the widget again
    txtLogs.config(state=tk.DISABLED)    

# Init
# Make sure temp folders exists
if not os.path.isdir(RAW_FOLDER):
    os.mkdir(RAW_FOLDER)
    
if not os.path.isdir(MERGED_FOLDER):
    os.mkdir(MERGED_FOLDER)

def test_function():
    # Some initial code
    insertLog("Starting function...")

    condition1 = True
    condition2 = False

    if condition1:
        insertLog("Condition 1 is True")
        if condition2:
            insertLog("Condition 2 is True")
            return  # Exit the function here
        else:
            insertLog("Condition 2 is False")

    # Common exit code
    insertLog("Executing common exit code...")

# Function to list files in a directory
def list_files_in_directory():
    insertLog(f'Listing files in {MERGED_FOLDER} folder.')
    try:
        # List all files in the directory
        files = [f for f in os.listdir(MERGED_FOLDER) if os.path.isfile(os.path.join(MERGED_FOLDER, f))]
        
        
        if not files:  # If no files are found            
            insertLog("No files found in the selected folder.\n")
        else:
            # Sort files by name (alphabetically)
            sorted_files = sorted(files)
            
            for file in sorted_files:
                if not file.startswith('.'):
                    insertLog(file)
        insertLog('------------------\nEnd')
    except Exception as e:
        insertLog(f'Error: {e}')

# **********************************
# Create the main application window
# **********************************
root = tk.Tk()
root.title("YouTube Video Downloader")
# root.geometry("700x400")
root.configure(bg="#FFFFFF")

frame_poToken = tk.Frame()
frame_poToken.configure(bg="#FFFFFF")
frame_poToken.pack(padx=10, pady=10)

# add visitor, poToken
lbl_visitor = tk.Label(frame_poToken, text="visitor")
lbl_visitor.grid(row=0,column=0)

txt_visitor = tk.Entry(frame_poToken, width=55)
txt_visitor.grid(row=0,column=1, columnspan=3)

lbl_poToken = tk.Label(frame_poToken, text="poToken")
lbl_poToken.grid(row=1,column=0)

txt_poToken = tk.Entry(frame_poToken, width=55)
txt_poToken.grid(row=1,column=1, columnspan=3)

frame = tk.Frame()
frame.configure(bg="#FFFFFF")
frame.pack(padx=5, pady=10)

# Label and Entry for the YouTube URL
url_label = tk.Label(frame, text="YouTube URL:")
url_label.grid(row=0, column=0, padx=2, pady=5)

txturl = tk.Entry(frame, width=50)
txturl.grid(row=0, column=1, padx=2, pady=5)

# Button to start the download
download_button = tk.Button(frame, text="Download", command=start_download)
download_button.grid(row=0, column=2, padx=2, pady=5)

# Multiline Textbox for progress updates

txtLogs = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
txtLogs.grid(row=1, column=0, columnspan=3, pady=5)
txtLogs.configure(state=tk.DISABLED)

# Frame for buttons below the logs
frame_btn = tk.Frame(root, bg="#FFFFFF")
frame_btn.pack(pady=(5, 10))  # Add padding: 10px top, 20px bottom

# Add empty columns on both sides to center the buttons
frame_btn.grid_columnconfigure(0, weight=1)  # Empty column on the left
frame_btn.grid_columnconfigure(3, weight=1)  # Empty column on the right

btnListFiles = tk.Button(frame_btn, text="Downloaded Files", command=list_files_in_directory)
btnListFiles.grid(row=0, column=1)
# btnListFiles.pack(side=tk.TOP, anchor=tk.CENTER)  # Center the button

btn_clear_logs = tk.Button(frame_btn, text="Clear Logs", command=clearLogs)
btn_clear_logs.grid(row=0, column=2)
# btn_clear_logs.pack(side=tk.TOP, anchor=tk.CENTER)  # Center the button

# Schedule the initialization function to run after the GUI starts
insertLog('Getting poToken...')
download_button.config(state=tk.DISABLED)
root.after(0, get_po_token)

# Run the application
root.mainloop()