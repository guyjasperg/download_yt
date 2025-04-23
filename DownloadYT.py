#!/usr/bin/env python3

from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog  # For folder selection dialog
from tkinter import messagebox
import cv2
import vlc
from PIL import Image, ImageTk
import pygame  # For video/audio playback
from pynput import keyboard

from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from UtilityFunctions import *
import pychrome, html
import os, subprocess, threading, queue, platform
import json  # For parsing JSON
import sys
import time
import configparser
# import webview

import requests
import sqlite3

# Read settings from config.ini file
# Read settings from config.ini file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
print((config_path))
config.read(config_path)

RAW_FOLDER = config.get('PATHS', 'RAW_FOLDER') #, fallback='DOWNLOADS/')
MERGED_FOLDER = config.get('PATHS', 'MERGED_FOLDER') #, fallback='NEW_SONGS/')
PARAM_WEB = config.getboolean('PATHS', 'PARAM_WEB', fallback=False)
PARAM_PO_TOKEN = config.getboolean('PATHS', 'PARAM_PO_TOKEN', fallback=False)

# print('RAW_FOLDER',RAW_FOLDER)
# print('MERGED_FOLDER',MERGED_FOLDER)

# SOUND_NOTIF = './Sounds/arpeggio-467.mp3'
# SOUND_ERROR = './Sounds/glitch-notification.mp3'
# SOUND_PROCESS_COMPLETE = './Sounds/hitech-logo.mp3'

# need to use youtube-po-token-generator to generate poToken and visitorData
# js_url =  './youtube-po-token-generator/examples/one-shot.js'
js_url =  './one-shot.js'
VISITOR_DATA = 'CgtKbVR3aVJQUTUxcyic5fy8BjIKCgJQSBIEGgAgbg%3D%3D'
PO_TOKEN = 'MnRH5JFMhu5OqUfcnrah0Bf_GmXlDOP08QPu9RFMLSJtZQRocmea4VGzTCEgMfoGXur3S_IdichbZKmYiEUtWqG5wY4dj29DAypotNrsSry0NvUr8Zk16KWsr1ulG2oXvCRJ_8JsERbT3FzT2DaT1ONpPvVopA=='

# Flag to track if a download is in progress
is_downloading = False
video_filename = ""
audio_filename = ""
url_title_map = {}  # Dictionary to store URLs (key) and titles (value)
yt = None

# Queue for thread-safe communication
message_queue = queue.Queue()

# Init
# Make sure temp folders exists
if not os.path.isdir(RAW_FOLDER):
    os.mkdir(RAW_FOLDER)
if not os.path.isdir(MERGED_FOLDER):
    os.mkdir(MERGED_FOLDER)

# Shared event to signal the listener to stop
stop_event = threading.Event()

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
            ys.download(filename=video_filename, output_path=RAW_FOLDER)

        if audiostream:
            #title = audiostream.default_filename
            message_queue.put(f"\n[{audio_filename}]\n")
            ys = yt.streams.get_by_itag(audiostream.itag)
            ys.download(filename=audio_filename, output_path=RAW_FOLDER)

        return True
    except Exception as e:
        message_queue.put(f"ERROR: An error occurred downloading files. [{e}]")
        return False

# def play_sound_threaded(file_path):
#     if not os.path.exists(file_path):
#         insertLog(f"play_sound Error: File '{file_path}' not found.")
#         return

#     try:
#         if sys.platform == "darwin":  # macOS
#             subprocess.run(["afplay", file_path], check=True)
#         elif sys.platform == "win32":  # Windows
#             import winsound
#             winsound.PlaySound(file_path, winsound.SND_FILENAME)
#         elif sys.platform.startswith("linux"):  # Linux
#             subprocess.run(["aplay", file_path], check=True)
#         else:
#             insertLog("play_sound: Unsupported operating system.")
#     except Exception as e:
#         insertLog(f"Error playing sound: {e}")    
#     # os.system("afplay ./arpeggio-467.mp3")
    
# # Function to play sound in a separate thread
# def play_sound(file_path):
#     threading.Thread(target=play_sound_threaded, args=(file_path,), daemon=True).start()
    
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
        
def start_download_thread(bDownloadAll, url, tab_id):
    global video_filename
    global audio_filename
    global yt
    global is_downloading
    global PO_TOKEN, VISITOR_DATA
    
    if bDownloadAll:
        # If bDownloadAll is True, iterate over all URLs in url_title_map
        ctr = 0
        for url, title in url_title_map.items():
            ctr += 1
            message_queue.put(f"Downloading: [{ctr}/{len(url_title_map)}]\n")
            tab_id = title.split('|')[1].strip() if '|' in title else ""
            is_downloading = True
            process_queue()  # Process the queue after each download
            start_download_thread(False, url, tab_id)  # Call with bDownloadAll=False for each URL
            message_queue.put("-----------------------------------\n")
            # is_downloading = False
        
        message_queue.put("Done downloading all URLs.")
        return  # Exit after processing all URLs
    
    try:
        try:
            message_queue.put("contacting server...\n")
            
            # modified YouTube class to use po_token paramater            
            # yt = YouTube(url,'WEB', po_token=PO_TOKEN, visitor_data=VISITOR_DATA, on_progress_callback=on_progress )
            # yt = YouTube(url,use_po_token=True,po_token=PO_TOKEN, on_progress_callback=on_progress )
            # yt = YouTube(url, on_progress_callback=on_progress )
            # yt = YouTube(url, po_token=PO_TOKEN, on_progress_callback=on_progress )
            # yt = YouTube(url, 'WEB', on_progress_callback=on_progress )
            
            print(f'PARAM_WEB: {PARAM_WEB}, PARAM_PO_TOKEN: {PARAM_PO_TOKEN}')
            
            if PARAM_WEB and PARAM_PO_TOKEN:
                yt = YouTube(url, 'WEB', po_token=PO_TOKEN, on_progress_callback=on_progress )
            elif PARAM_WEB:
                yt = YouTube(url, 'WEB', on_progress_callback=on_progress )
            elif PARAM_PO_TOKEN:
                yt = YouTube(url, po_token=PO_TOKEN, on_progress_callback=on_progress )
            else:
                yt = YouTube(url, on_progress_callback=on_progress )
                
        except Exception as e:
            message_queue.put(f"ERROR: An error occurred: {e}")
            if not bDownloadAll:
                is_downloading = False
            return
        
        # continue
        message_queue.put(f'YT Title: {yt.title}')
        #select highest resolution video
        # Sort streams by resolution in descending order
        selectedVideoStream = None
        sorted_streams = sorted(yt.streams.filter(type="video"), key=lambda s: s.resolution) 
        # message_queue.put(f"Total video streams: {len(sorted_streams)}")
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
            video_filename = f"{remove_keywords(selectedVideoStream.default_filename)}"
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
            audio_filename = f"{remove_keywords(selectedAudioStream.default_filename)}"
            message_queue.put(f"selected audio stream: [{selectedAudioStream.itag}] {selectedAudioStream.abr}\n")
        else:
            message_queue.put("No audio stream selected")

        # message_queue.put("\nDownloading files...")       
        if Downloadfiles(selectedVideoStream, selectedAudioStream) == False:
            message_queue.put('Download failed.')
            if not bDownloadAll:
                is_downloading = False
            return
        
        # successful download, proceed processing
        # Merge video and audio files
        if selectedAudioStream != None:
            message_queue.put("\nMerging audio and video streams...")

            # Combine video and audio using ffmpegexit            
            output_file = f"{MERGED_FOLDER}{to_title_case(video_filename)}"
            message_queue.put(f"saving file to ->{output_file}")

            if os.path.isfile(output_file):
                message_queue.put("File already exists!")
                if not bDownloadAll:
                    is_downloading = False
                return
            
            ffmpeg_path = config.get('PATHS', 'FFMPEG_PATH', fallback='') 
            if ffmpeg_path == '':
                message_queue.put("FFMPEG_PATH not set in config.ini")
                ffmpeg_path = 'ffmpeg'

            command = [
                f'{ffmpeg_path}',
                '-i', f"{RAW_FOLDER}{video_filename}",
                '-i', f"{RAW_FOLDER}{audio_filename}",
                '-loglevel', 'warning',
                '-preset', 'ultrafast',  # Use ultrafast preset for faster encoding
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
            play_sound(SOUND_NOTIF)   
            
            # close tab
            if tab_id != "" :
                message_queue.put(f'closing tab [{tab_id}]')
                browser = pychrome.Browser()
                browser.close_tab(tab_id)  
    except Exception as e:
        message_queue.put(f"Error: {str(e)}")
        play_sound(SOUND_ERROR)
    finally:
        # Reset the downloading flag
        message_queue.put('-thread_download_video')
        if not bDownloadAll:
            is_downloading = False

def start_download():
    global is_downloading

    # Ask the user if they want to download all entries from the combo box
    # use url_title_map to get all the urls
    url_count = len(url_title_map)
    download_all = False
    if url_count > 1:
        download_all = messagebox.askyesno(
            "Download All?",
            "Do you want to download all entries from the combo box?"
        )

    if url_count > 1 and download_all:        
        clearLogs()
        
        # disable button to prevent disrupting current process
        download_button.config(state=tk.DISABLED)
        
        is_downloading = True
        
        # Run the download in a separate thread
        threading.Thread(target=start_download_thread, args=(True,'',''), daemon=True).start()

        # wait for download to finish before proceeding to next download
        process_queue()
        # while is_downloading:
        #     # root.after(100, process_queue)  # Check the queue again after 100ms
        #     process_queue()
        #     # root.update_idletasks()  # Ensure the UI updates
        #     # time.sleep(0.1)  # Add a small delay to prevent busy-waiting

        # # Process next download
        # insertLog("----------------------------\n\n")

    else:
        # single download
        # Find the URL corresponding to the selected title (linear search, could be optimized if needed)
        selected_title = cboURL.get()
        selected_url = selected_title
        tab_id = ""
        if len(cboURL.cget('values')) > 0:
            for url, title in url_title_map.items():
                if title == selected_title:
                    selected_url = url
                    break  # Stop searching once found
            tab_id = selected_title.split('|')[1].strip()
        print(f"Selected URL: {selected_url}, tab_id: {tab_id}")        
        
        # check if there is valid input
        url = selected_url
        if url:
            clearLogs()
            
            insertLog(f'YT url: {url}')
            
            # Set the downloading flag
            is_downloading = True
            
            # Run the download in a separate thread
            threading.Thread(target=start_download_thread, args=(False, url,tab_id,), daemon=True).start()
                    
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
    insertLog(f'Listing files in\n[{MERGED_FOLDER}]\nfolder.')
    insertLog('------------------')        
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

def populate_combobox():
    global url_title_map  # Access the global tab data
    
    titles = list(url_title_map.values()) 
    cboURL['values'] = titles  # Set the combobox values (titles)
    
    if titles:
        cboURL.bind("<<ComboboxSelected>>", on_select)  # Bind the selection event
        cboURL.config(state="readonly")
        cboURL.current(0)
        on_select(None)
    else:
        cboURL.config(state="normal")
    
    # if cboURL["values"]: # selects the first item if available
    #     cboURL.current(0)
    #     on_select(None)

def on_select(event):
    """Handles Combobox selection and opens URL."""
    global tab_data
    selected_title = cboURL.get()
    print(f"SelectedItem: {selected_title}")

def get_selected():
    selected_title = cboURL.get()
    print(f"SelectedItem: {selected_title}")

####################################
# pychrome related functions
####################################
url_title_map = {}  # Declare the global dictionary

def check_and_run_chrome():
    if not check_chrome_running():
        response = messagebox.askyesno("Chrome with Debugging", "Do you want to run Chrome with debugging?")
        if response:  # True if Yes, False if No
            launch_chrome_with_debugging()
        else:
            print("User clicked No")
    else:
        # Get opened tabs
        browser = pychrome.Browser()
        
        try:
            tabs = browser.list_tab()
            global url_title_map  # Dictionary to store URLs (key) and titles (value)
            url_title_map.clear()

            for tab in tabs:
                if tab._kwargs.get('type') == 'page':
                    # Access tab information
                    url = tab._kwargs.get('url')
                    if url and "youtube.com/watch?" in url:
                        title = f'{tab._kwargs.get('title')} | {tab.id}'
                        print(title)
                        url_title_map[url] = html.unescape(title)  # URL is the key now
            
            if url_title_map:
                populate_combobox()

            #make sure Download button is enabled
            download_button.config(state=tk.NORMAL)

        except Exception as e:
            message = str(e)
            if message.find('Failed to establish a new connection')>=0:
                print("Chrome with debugging not running")
            else:
                print(f"An error occurred: {e}")

def check_chrome_running():
    """Checks if a Chrome instance with remote debugging is running."""
    bChromeRunning = False
    try:
        browser = pychrome.Browser()  # Try connecting; if it fails, Chrome isn't running or debugging is off
        browser.list_tab() # close the browser.
        bChromeRunning = True  # Chrome with debugging is running
    except Exception as e:
        print('ERROR: check_chrome_running() ', e)

    print('Chrome Running:', bChromeRunning)
    return bChromeRunning

def launch_chrome_with_debugging(port=9222):
    """Launches Chrome with remote debugging enabled."""
    chrome_executable = None

    # Find Chrome executable (platform-specific)
    if os.name == 'nt':  # Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            # Add more potential paths if needed
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_executable = path
                break
    elif os.name == 'posix':  # macOS/Linux
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
            "/usr/bin/google-chrome",  # Common Linux path
            "/usr/bin/chromium-browser", # Common Linux path
            # Add more potential paths if needed
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_executable = path
                break

    if not chrome_executable:
        raise Exception("Chrome executable not found. Please specify the path.")

    try:
        subprocess.Popen([
            chrome_executable,
            "--remote-debugging-port=" + str(port),
            "--user-data-dir=./chrome_profile", # Use a specific profile to avoid conflicts
            "--no-first-run", # prevent first run screen
            "--disable-extensions", # prevent extensions from interfering
        ])

        # Give Chrome a little time to start
        time.sleep(2)  # Adjust if needed

        return True

    except FileNotFoundError:
        raise Exception(f"Chrome executable not found at: {chrome_executable}")
    except Exception as e:
        raise Exception(f"Error launching Chrome: {e}")

def make_button_transparent(style):
    style.configure("TButton", relief="flat", background=root.cget("background"), borderwidth=0)
    style.map("TButton",
              background=[("active", root.cget("background"))],
              foreground=[("active", "blue")])

def open_downloads_folder():
    """Opens the downloaded songs folder in Finder/Explorer."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", MERGED_FOLDER])
        elif sys.platform == "win32":  # Windows
            os.startfile(MERGED_FOLDER)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["xdg-open", MERGED_FOLDER])
        else:
            insertLog("Unsupported operating system for opening folders.")
    except Exception as e:
        error_msg = f"Error opening folder: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)

def get_db_path():
    """Get the path to the SQLite database file."""
    return config.get('PATHS', 'DATABASE_PATH', fallback='mydatabase.sqlite')

def get_server_url():
    """Get the appropriate server URL based on production mode."""
    if production_var.get():
        return config.get('PATHS', 'PROD_SERVER_URL', fallback='')
    return config.get('PATHS', 'SERVER_URL', fallback='')

def get_upload_url():
    """Get the appropriate upload URL based on production mode."""
    if production_var.get():
        return config.get('PATHS', 'PROD_SERVER_URL_UPLOAD', fallback='')
    return config.get('PATHS', 'SERVER_URL_UPLOAD', fallback='')

def get_param_WEB():
    return config.getboolean('PATHS', 'PARAM_WEB', fallback=False)

def get_param_PO_TOKEN():
    return config.getboolean('PATHS', 'PARAM_PO_TOKEN', fallback=False)

def get_config_settings():
    global RAW_FOLDER, MERGED_FOLDER, PARAM_WEB, PARAM_PO_TOKEN
    
    RAW_FOLDER = config.get('PATHS', 'RAW_FOLDER') #, fallback='DOWNLOADS/')
    MERGED_FOLDER = config.get('PATHS', 'MERGED_FOLDER') #, fallback='NEW_SONGS/')
    PARAM_WEB = config.getboolean('PATHS', 'PARAM_WEB', fallback=False)
    PARAM_PO_TOKEN = config.getboolean('PATHS', 'PARAM_PO_TOKEN', fallback=False)
    
def search_database():
    """Search the database based on the query in the search box."""
    query = txt_search.get().strip()
    if not query:
        messagebox.showwarning("Warning", "Please enter a search query.")
        return

    try:
        # Clear existing items in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Connect to the database
        db_path = get_db_path()
        if not os.path.exists(db_path):
            messagebox.showerror("Error", "Database file not found. Please download the database first.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Search in both artist and title columns
        search_query = f"%{query}%"
        cursor.execute("""
            SELECT songid, artist, title, path, starttime 
            FROM dbsongs 
            WHERE artist LIKE ? OR title LIKE ?
            ORDER BY artist, title
        """, (search_query, search_query))

        # Add results to the treeview
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

        conn.close()

        # Show message if no results found
        if not tree.get_children():
            messagebox.showinfo("Search Results", "No matching songs found.")
            root.lift()  # Bring the main window to the front
            root.focus_force()  # Ensure the main window is focused
            txt_search.focus_set()
            txt_search.select_range(0, tk.END)  # Select all text in the search box

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error searching database: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

def download_database():
    """Download the songs database from the server."""
    try:
        server_url = get_server_url()
        if not server_url:
            messagebox.showerror("Error", "Server URL not configured. Please check configuration.")
            return

        # Download the database file
        response = requests.get(server_url)
        response.raise_for_status()

        # Save the downloaded file
        with open(get_db_path(), 'wb') as f:
            f.write(response.content)

        messagebox.showinfo("Success", "Database downloaded successfully!")
        
        # Clear and refresh the search results if there was a previous search
        if txt_search.get().strip():
            search_database()

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Download Error", f"Error downloading database: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

def upload_database():
    """Upload the songs database to the server."""
    # Create a processing dialog
    processing_dialog = DialogProcessing(root, title="Uploading Database", message="Uploading database, please wait...")

    # Run the upload in a separate thread
    def upload_task():
        try:
            upload_url = get_upload_url()
            if not upload_url:
                messagebox.showerror("Error", "Upload URL not configured. Please check configuration.")
                return

            db_path = get_db_path()
            if not os.path.exists(db_path):
                messagebox.showerror("Error", "Database file not found.")
                return

            # Upload the database file
            with open(db_path, 'rb') as f:
                response = requests.post(upload_url, files={'dbFile': f})
                response.raise_for_status()

            processing_dialog.update_message('Database uploaded successfully!', SOUND_NOTIF)
            # messagebox.showinfo("Success", "Database uploaded successfully!")

        # except requests.exceptions.RequestException as e:
        #     messagebox.showerror("Upload Error", f"Error uploading database: {str(e)}")
        except Exception as e:
            processing_dialog.update_message(f"An unexpected error occurred.", SOUND_ERROR)
            insertLog(f"URL: {get_upload_url()}")   
            insertLog(f"Error uploading database: {str(e)}")
            # messagebox.showerror("Upload Error", f"An unexpected error occurred: {str(e)}")
        finally:
            processing_dialog.toggle_close_button(enable=True)

    threading.Thread(target=upload_task, daemon=True).start()

def edit_song_details():
    """Edit the selected song's details."""
    if not tree.selection():
        return
        
    item = tree.selection()[0]
    song_id = tree.item(item)['values'][0]
    old_artist = tree.item(item)['values'][1]
    old_title = tree.item(item)['values'][2]
    old_filepath = tree.item(item)['values'][3]
    old_starttime = tree.item(item)['values'][4]
    
    # Show edit dialog
    dialog = DialogSongEdit(root, old_artist, old_title, old_filepath, old_starttime)
    root.wait_window(dialog.dialog)
    
    # If user clicked Save and provided new details
    if dialog.result:
        print(f"New details: {dialog.result}")
        try:
            # Connect to database
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            # Update the database
            cursor.execute("""
                UPDATE dbsongs 
                SET artist = ?, title = ?, path = ?, starttime = ?
                WHERE songid = ?
            """, (dialog.result['artist'], dialog.result['title'], dialog.result['filepath'], dialog.result['start_time'], song_id))
            
            conn.commit()
            conn.close()
            
            # Update the treeview
            tree.item(item, values=(
                song_id,
                dialog.result['artist'],
                dialog.result['title'],
                dialog.result['filepath'],
                dialog.result['start_time']
            ))
            
            insertLog(f"Updated song details for ID {song_id}")
            
        except sqlite3.Error as e:
            error_msg = f"Database error: {str(e)}"
            insertLog(error_msg)
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            insertLog(error_msg)
            messagebox.showerror("Error", error_msg)

def delete_song():
    """Delete the selected song from the database."""
    if not tree.selection():
        return
        
    item = tree.selection()[0]
    song_id = tree.item(item)['values'][0]
    artist = tree.item(item)['values'][1]
    title = tree.item(item)['values'][2]
    filepath = tree.item(item)['values'][3]
    
    # Show confirmation dialog
    if not messagebox.askyesno("Confirm Delete", 
        f"Are you sure you want to delete this song?\n\nArtist: {artist}\nTitle: {title}"):
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Delete the song
        cursor.execute("DELETE FROM dbsongs WHERE songid = ?", (song_id,))
        conn.commit()
        conn.close()
        
        insertLog(f"Deleted song: {artist} - {title}")

        # Remove from treeview
        tree.delete(item)
        
        # Delete the actual file from the filesystem
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                insertLog(f"Error deleting file: {str(e)}")
                messagebox.showerror("Error", f"Error deleting file: {str(e)}")
        insertLog(f"Deleted file: {filepath}")
        
    except sqlite3.Error as e:
        error_msg = f"Database error: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)

def show_db_context_menu(event):
    """Show the context menu for database entries on right click."""
    item = tree.identify_row(event.y)
    if item:
        tree.selection_set(item)
        db_context_menu.post(event.x_root, event.y_root)


class DialogConfig:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration")
        self.dialog.transient(parent)  # Make dialog modal
        self.dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on the parent window
        window_width = 500
        window_height = 435  # Increased height to accommodate new entry
        screen_width = parent.winfo_x() + parent.winfo_width() // 2
        screen_height = parent.winfo_y() + parent.winfo_height() // 2
        x = screen_width - window_width // 2
        y = screen_height - window_height // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create and pack the widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Folder paths
        ttk.Label(frame, text="Raw Downloads Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.raw_folder = ttk.Entry(frame, width=50)
        self.raw_folder.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        self.raw_folder.insert(0, RAW_FOLDER)
        
        ttk.Label(frame, text="Merged Files Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.merged_folder = ttk.Entry(frame, width=50)
        self.merged_folder.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        self.merged_folder.insert(0, MERGED_FOLDER)
        
        # Database path
        ttk.Label(frame, text="Database Path:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.database_path = ttk.Entry(frame, width=50)
        self.database_path.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        self.database_path.insert(0, config.get('PATHS', 'DATABASE_PATH', fallback='mydatabase.sqlite'))
        
        # Server URLs
        ttk.Label(frame, text="Development Server URL:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.server_url = ttk.Entry(frame, width=50)
        self.server_url.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        self.server_url.insert(0, config.get('PATHS', 'SERVER_URL', fallback=''))
        
        ttk.Label(frame, text="Production Server URL:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.prod_server_url = ttk.Entry(frame, width=50)
        self.prod_server_url.grid(row=4, column=1, sticky=tk.EW, pady=5, padx=5)
        self.prod_server_url.insert(0, config.get('PATHS', 'PROD_SERVER_URL', fallback=''))
        
        ttk.Label(frame, text="Development Upload URL:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.upload_url = ttk.Entry(frame, width=50)
        self.upload_url.grid(row=5, column=1, sticky=tk.EW, pady=5, padx=5)
        self.upload_url.insert(0, config.get('PATHS', 'SERVER_URL_UPLOAD', fallback=''))
        
        ttk.Label(frame, text="Production Upload URL:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.prod_upload_url = ttk.Entry(frame, width=50)
        self.prod_upload_url.grid(row=6, column=1, sticky=tk.EW, pady=5, padx=5)
        self.prod_upload_url.insert(0, config.get('PATHS', 'PROD_SERVER_URL_UPLOAD', fallback=''))
        
        # FFMPEG Path
        ttk.Label(frame, text="FFMPEG Path:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.ffmpeg_path = ttk.Entry(frame, width=50)
        self.ffmpeg_path.grid(row=7, column=1, sticky=tk.EW, pady=5, padx=5)
        self.ffmpeg_path.insert(0, config.get('PATHS', 'FFMPEG_PATH', fallback='ffmpeg'))
        
        # Python3 Path
        ttk.Label(frame, text="Python3 Path:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.python3_path = ttk.Entry(frame, width=50)
        self.python3_path.grid(row=8, column=1, sticky=tk.EW, pady=5, padx=5)
        self.python3_path.insert(0, config.get('PATHS', 'PYTHON3_PATH', fallback='/usr/bin/python3'))
        
        # pyTube Params
        ttk.Label(frame, text="pyTube Params:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.param_web = tk.BooleanVar(value=config.getboolean('PATHS', 'param_web', fallback=False))
        self.param_po_token = tk.BooleanVar(value=config.getboolean('PATHS', 'param_po_token', fallback=False))
        
        # frame for the check boxes
        frame_pytube_params = ttk.Frame(frame)
        frame_pytube_params.grid(row=9, column=1, columnspan=1, sticky=tk.EW, pady=5)

        self.chk_web = ttk.Checkbutton(frame_pytube_params, text="WEB", variable=self.param_web)
        self.chk_web.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        self.chk_po_token = ttk.Checkbutton(frame_pytube_params, text="PO Token", variable=self.param_po_token)
        self.chk_po_token.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=10, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save_config).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
    def save_config(self):
        """Save the configuration to config.ini file."""
        global RAW_FOLDER, MERGED_FOLDER
        
        try:
            # Update config object
            if not config.has_section('PATHS'):
                config.add_section('PATHS')
                
            config.set('PATHS', 'RAW_FOLDER', self.raw_folder.get())
            config.set('PATHS', 'MERGED_FOLDER', self.merged_folder.get())
            config.set('PATHS', 'DATABASE_PATH', self.database_path.get())
            config.set('PATHS', 'SERVER_URL', self.server_url.get())
            config.set('PATHS', 'PROD_SERVER_URL', self.prod_server_url.get())
            config.set('PATHS', 'SERVER_URL_UPLOAD', self.upload_url.get())
            config.set('PATHS', 'PROD_SERVER_URL_UPLOAD', self.prod_upload_url.get())
            config.set('PATHS', 'FFMPEG_PATH', self.ffmpeg_path.get())
            config.set('PATHS', 'PYTHON3_PATH', self.python3_path.get())
            config.set('PATHS', 'PARAM_WEB', str(self.param_web.get()))
            config.set('PATHS', 'PARAM_PO_TOKEN', str(self.param_po_token.get()))
            
            # Save to file
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
                
            # Update global variables
            get_config_settings()
            # RAW_FOLDER = self.raw_folder.get()
            # MERGED_FOLDER = self.merged_folder.get()
            
            # Create directories if they don't exist
            os.makedirs(RAW_FOLDER, exist_ok=True)
            os.makedirs(MERGED_FOLDER, exist_ok=True)
            
            # Reload configuration
            config.read('config.ini')
            
            # Update folder path in file management tab
            txt_folder.delete(0, tk.END)
            txt_folder.insert(0, MERGED_FOLDER)
            refresh_file_list()
            
            messagebox.showinfo("Success", "Configuration saved and reloaded successfully!")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration: {str(e)}")

def open_config_dialog():
    """Open the configuration dialog."""
    dialog = DialogConfig(root)
    root.wait_window(dialog.dialog)

def refresh_file_list():
    """Refresh the file list in the treeview."""
    folder_path = txt_folder.get()
    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Invalid folder path")
        return
        
    # Clear existing items
    for item in file_tree.get_children():
        file_tree.delete(item)
        
    # Add files to treeview
    try:
        files = []
        for file in os.listdir(folder_path):
            # Skip hidden files (starting with .)
            if file.startswith('.'):
                continue
                
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                # Get file stats
                stats = os.stat(file_path)
                size_bytes = stats.st_size
                size = f"{size_bytes / 1024 / 1024:.2f} MB"
                modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                
                # Store the raw values for sorting
                files.append({
                    'name': file,
                    'size_bytes': size_bytes,
                    'size_display': size,
                    'modified_timestamp': stats.st_mtime,
                    'modified_display': modified
                })
        
        # Sort files by name initially
        files.sort(key=lambda x: x['name'].lower())
        
        # Add sorted files to treeview
        for file_info in files:
            file_tree.insert('', 'end', values=(
                file_info['name'],
                file_info['size_display'],
                file_info['modified_display']
            ), tags=(str(file_info['size_bytes']), str(file_info['modified_timestamp'])))
            
        # Update file count
        lbl_file_count.config(text=f"Files: {len(files)}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Error reading folder: {str(e)}")

def add_songs_to_db():
    """Add new songs from the file list to the database."""
    # First check if there are any files in the list
    if not file_tree.get_children():
        messagebox.showwarning("Warning", "No files found in the current folder.")
        return
        
    try:
        # Get the database path
        db_path = get_db_path()
        if not os.path.exists(db_path):
            messagebox.showerror("Error", "Database file not found. Please download the database first.")
            return

        # Get the folder path
        folder_path = txt_folder.get()
        if not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Invalid folder path")
            return

        # Get the selected filename format
        selected_format = filename_format.get()

        # Get all songs from DB with same folder
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM dbsongs where path like ? order by path", (f"{folder_path}%",))    
        rows = cursor.fetchall()
        data_in_db = sorted([row[0] for row in rows])
        
        # Get all files in folder        
        files_in_folder = get_files_in_directory(folder_path)
        
        # Get new files not yet in DB
        new_files = find_new_files(data_in_db, files_in_folder)
        
        # Initialize list to store songs to add
        songs_to_add = []
        
        insertLog(f"New files to add: {len(new_files)}")
            
        for file in new_files:
            filename = os.path.basename(file)
            filename_no_ext = os.path.splitext(filename)[0]
            
            # Count number of hyphens in filename
            hyphen_count = filename_no_ext.count('-')
            
            if hyphen_count == 1:
                # Parse according to selected format
                parts = filename_no_ext.split('-', 1)
                if len(parts) == 2:
                    if selected_format == "Artist - Title":
                        artist = parts[0].strip()
                        title = parts[1].strip()
                    else:  # Title - Artist
                        title = parts[0].strip()
                        artist = parts[1].strip()
                    
                    duration = get_video_duration(file)
                    # insertLog(f'Artist: {artist}, Title: {title}, Duration: {duration}')
                    songs_to_add.append((artist, title, file, duration))
                else:
                    # Show dialog if parsing fails
                    dialog = DialogArtistTitle(root, filename)
                    root.wait_window(dialog.dialog)
                    
                    if dialog.result:
                        duration = get_video_duration(file)
                        artist = dialog.result['artist']
                        title = dialog.result['title']
                        # insertLog(f'Artist: {artist}, Title: {title}, Duration: {duration}')
                        songs_to_add.append((artist, title, file, duration))
                    else:
                        insertLog(f"Skipped file: {filename}")
            else:
                # Multiple hyphens or no hyphen, show dialog
                dialog = DialogArtistTitle(root, filename)
                root.wait_window(dialog.dialog)
                
                if dialog.result:  # If user entered data and clicked Save
                    duration = get_video_duration(file)
                    artist = dialog.result['artist']
                    title = dialog.result['title']
                    insertLog(f'Artist: {artist}, Title: {title}, Duration: {duration}')
                    songs_to_add.append((artist, title, file, duration))
                else:
                    insertLog(f"Skipped file: {filename}")
                
        if songs_to_add:
            insertLog('Saving to database...')
            for i, (artist, title, file, duration) in enumerate(songs_to_add, 1):
                insertLog(f"Song {i}/{len(songs_to_add)}: Artist: {artist}, Title: {title}, Duration: {duration}")
            
            try:
                # Begin transaction
                conn.execute("BEGIN TRANSACTION;")
                
                # Insert songs into database
                cursor.executemany("INSERT INTO dbsongs (artist, title, path, duration) VALUES (?, ?, ?, ?);", songs_to_add)
                
                # Commit transaction
                conn.commit()
                conn.close()
                insertLog(f"Inserted {len(songs_to_add)} new songs into the database.")
                
            except Exception as e:
                insertLog(f"Error saving to database: {e}")
                if conn:
                    conn.close()
        
        # Show success message
        messagebox.showinfo("Success", "Songs have been added to the database.")
        
    except Exception as e:
        error_msg = f"Error adding songs to database: {str(e)}"
        messagebox.showerror("Error", error_msg)
        insertLog(error_msg)

def browse_folder():
    """Open folder selection dialog and update the folder path."""
    folder_path = filedialog.askdirectory(initialdir=txt_folder.get())
    if folder_path:  # If a folder was selected
        txt_folder.delete(0, tk.END)
        txt_folder.insert(0, folder_path)
        refresh_file_list()  # Refresh the file list with the new folder

def preview_video():
    """Open video preview dialog for the selected file."""
    if not file_tree.selection():
        return
        
    item = file_tree.selection()[0]
    filename = file_tree.item(item)['values'][0]
    folder_path = txt_folder.get()
    filepath = os.path.join(folder_path, filename)
    
    if not filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
        messagebox.showwarning("Warning", "Selected file is not a video file.")
        return
    
    try:
        # open_file_with_default_app(filepath)
        preview_video(filepath)
        # dialog = VideoPreviewDialog(root, filepath)
        # root.wait_window(dialog.dialog)
    except Exception as e:
        error_msg = f"Error previewing video: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)

class DialogArtistTitle:
    def __init__(self, parent, filename):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enter Artist and Title")
        self.dialog.transient(parent)  # Make dialog modal
        self.dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on the parent window
        window_width = 400
        window_height = 150
        screen_width = parent.winfo_x() + parent.winfo_width()//2
        screen_height = parent.winfo_y() + parent.winfo_height()//2
        x = screen_width - window_width//2
        y = screen_height - window_height//2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create and pack the widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Show filename
        ttk.Label(frame, text="Filename:").grid(row=0, column=0, sticky=tk.W, pady=5)
        filename_label = ttk.Label(frame, text=filename)
        filename_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Add entry fields
        ttk.Label(frame, text="Artist:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_artist = ttk.Entry(frame, width=40)
        self.entry_artist.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        ttk.Label(frame, text="Title:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_title = ttk.Entry(frame, width=40)
        self.entry_title.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Skip", command=self.skip).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        # Store the result
        self.result = None
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save())
        # Bind Escape key to skip
        self.dialog.bind('<Escape>', lambda e: self.skip())
        
        # Set focus to artist entry
        self.entry_artist.focus_set()
        
    def save(self):
        """Save the entered details and close the dialog."""
        artist = self.entry_artist.get().strip()
        title = self.entry_title.get().strip()
        
        if artist and title:  # Only save if both fields are filled
            self.result = {
                'artist': artist,
                'title': title
            }
            self.dialog.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter both artist and title.")
            
    def skip(self):
        """Skip this file and close the dialog."""
        self.dialog.destroy()

def activate_tab(index=0):
    """Handle Command-2 hotkey."""
    notebook.select(index)
    # Trigger the <<NotebookTabChanged>> event manually
    notebook.event_generate("<<NotebookTabChanged>>")
    # Force the UI to update immediately
    root.update_idletasks()
    
# Global variabl1e to hold the listener object
keyboard_listener = None
pressed_keys = set()

def on_press(key):
    try:
        if key not in pressed_keys:
            print(f'Key {key.char} pressed')
            if key.char == '1' and keyboard.Key.cmd in pressed_keys:
                root.after(0, lambda: activate_tab(0))
            elif key.char == '2' and keyboard.Key.cmd in pressed_keys:
                root.after(0, lambda: activate_tab(1))
            elif key.char == '3' and keyboard.Key.cmd in pressed_keys:
                root.after(0, lambda: activate_tab(2))
            elif key.char == 'q' and keyboard.Key.cmd in pressed_keys:
                print('Exiting listener...')
                stop_event.set()
                return False  # Stop listener
            
    except AttributeError:
        print(f'Special key {key} pressed')

    pressed_keys.add(key)
    
def on_release(key):
    print(f'Key {key} released')
    
    if key in pressed_keys:
        pressed_keys.remove(key)

def start_keyboard_listener():
    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    
    while not stop_event.is_set():
        keyboard_listener.join(timeout=0.1)  # Poll the stop event every 0.1 seconds

def open_file_with_default_app(file_path):
    """
    Opens the specified file with its default application, handling
    cross-platform compatibility and common errors.

    Args:
        file_path (str): The path to the file to open.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)  # Simplified for Windows
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif system == "Linux":
            # Use xdg-open, and check if it exists
            if subprocess.run(["which", "xdg-open"], capture_output=True, check=True).returncode == 0:
                subprocess.run(["xdg-open", file_path], check=True)
            else:
                print("xdg-open is not available.  Please install it, or use your desktop environment's file opener.")
                sys.exit(1) # exit, because we cannot open the file.
        else:
            print(f"Unsupported operating system: {system}")
            sys.exit(1) # exit, because we cannot open the file.

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error opening file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
            
# **********************************
# Create the main application window
# **********************************
root = tk.Tk()
root.title("YouTube Video Downloader")

#Hotkey bindings
# root.bind("<Option-1>", lambda e: activate_tab(0))
# root.bind('<Option-2>', lambda e: activate_tab(1))
# root.bind('<Option-3>', lambda e: activate_tab(2))

style = ttk.Style(root) #initialize style
style.theme_use('aqua')

# Set background color for all ttk widgets
bg_color = "#F0F0F0"  # Light gray background that matches ttk default
style.configure("TNotebook", background=bg_color)
style.configure("TFrame", background=bg_color)
style.configure("TLabel", background=bg_color)
style.configure("TButton", background=bg_color)
style.configure("Transparent.TLabel", background=bg_color)
style.map("TNotebook.Tab", background=[("selected", bg_color)])

# Configure Notebook style with border
style.configure("TNotebook", borderwidth=1)
style.configure("TNotebook.Tab", padding=[10, 4], font=('Helvetica', '10'))
style.configure("TFrame", borderwidth=0)  # Remove frame borders

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event):
        "Display text in tooltip window"
        self.x = event.x + self.widget.winfo_rootx() + 20
        self.y = event.y + self.widget.winfo_rooty() + 20
        if self.tipwindow or not self.text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (self.x, self.y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=4)

    def hide(self, event):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Create the notebook (tab control)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Create the first tab for existing functionality
tab_downloader = ttk.Frame(notebook)
notebook.add(tab_downloader, text='YouTube Downloader')

# Create the second tab for new features
tab_db_management = ttk.Frame(notebook)
notebook.add(tab_db_management, text='DB Management')

# Create the third tab for file management
tab_file_management = ttk.Frame(notebook)
notebook.add(tab_file_management, text='File Management')

# Create tooltips for each tab
for i, text in enumerate(["This is the first tab", "This is the second tab", "This is the third tab"]):
    tab_id = notebook.tabs()[i]
    tab_header = notebook.nametowidget(tab_id)
    Tooltip(tab_header, text)

# Add YouTube Downloader tab contents
frame_poToken = ttk.Frame(tab_downloader)
frame_poToken.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)
tab_downloader.grid_columnconfigure(0, weight=0)
tab_downloader.grid_columnconfigure(1, weight=0)

# add visitor, poToken
lbl_visitor = ttk.Label(frame_poToken, text="visitor")
lbl_visitor.grid(row=0,column=0, sticky=tk.W)

txt_visitor = ttk.Entry(frame_poToken, width=55)
txt_visitor.insert(tk.END, VISITOR_DATA)
txt_visitor.grid(row=0,column=1, columnspan=4)

lbl_poToken = ttk.Label(frame_poToken, text="poToken")
lbl_poToken.grid(row=1,column=0, sticky=tk.W)

txt_poToken = ttk.Entry(frame_poToken, width=55)
txt_poToken.insert(tk.END,PO_TOKEN)
txt_poToken.grid(row=1,column=1, columnspan=4)

frame = ttk.Frame(tab_downloader)
frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
# frame.configure(background="white")

tab_downloader.grid_rowconfigure(1, weight=1)
tab_downloader.grid_columnconfigure(0, weight=1)

# Label and Entry for the YouTube URL
url_label = ttk.Label(frame, text="YouTube Vid")
url_label.grid(row=0, column=0, padx=2, pady=5, sticky=tk.W)

cboURL = ttk.Combobox(frame)
cboURL.grid(row=0, column=1, padx=2, pady=5, sticky=tk.EW)

# New Button (before download_button)
btnRefreshTabs = ttk.Button(frame, text="..", command=check_and_run_chrome)
btnRefreshTabs.grid(row=0, column=2, padx=2, pady=5)

# Button to start the download
download_button = ttk.Button(frame, text="Download", command=start_download)
download_button.grid(row=0, column=3, padx=2, pady=5)

frame.grid_rowconfigure(0, weight=1)
frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(1, weight=1)

# Multiline Textbox for progress updates
txtLogs = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
txtLogs.grid(row=1, column=0, columnspan=4, pady=5, sticky=tk.NSEW)
txtLogs.configure(state=tk.DISABLED)

# Frame for buttons below the logs
frame_btn = ttk.Frame(tab_downloader)
frame_btn.grid(row=2, column=0, sticky=tk.EW, pady=10)
tab_downloader.grid_rowconfigure(2, weight=0)

frame_btn.grid_columnconfigure(0, weight=1)  # Left spacing
frame_btn.grid_columnconfigure(4, weight=1)  # Right spacing

# Add buttons with equal spacing
btnListFiles = ttk.Button(frame_btn, text="Downloaded Files", command=list_files_in_directory)
btnListFiles.grid(row=0, column=1, padx=5)

btn_clear_logs = ttk.Button(frame_btn, text="Clear Logs", command=clearLogs)
btn_clear_logs.grid(row=0, column=2, padx=5)

btn_open_folder = ttk.Button(frame_btn, text="Open Folder", command=open_downloads_folder)
btn_open_folder.grid(row=0, column=3, padx=5)

# Configure the file management tab layout
frame_file_tools = ttk.Frame(tab_file_management)
frame_file_tools.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
tab_file_management.grid_columnconfigure(0, weight=1)

# Add file management controls
lbl_folder = ttk.Label(frame_file_tools, text="Folder:")
lbl_folder.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

txt_folder = ttk.Entry(frame_file_tools)
txt_folder.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
txt_folder.insert(0, MERGED_FOLDER)  # Set default folder
frame_file_tools.grid_columnconfigure(1, weight=1)

btn_browse = ttk.Button(frame_file_tools, text="Browse", command=browse_folder)
btn_browse.grid(row=0, column=2, padx=5, pady=5)

btn_refresh = ttk.Button(frame_file_tools, text="Refresh", command=refresh_file_list)
btn_refresh.grid(row=0, column=3, padx=5, pady=5)

# Create frame for file list
frame_file_list = ttk.Frame(tab_file_management)
frame_file_list.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
tab_file_management.grid_rowconfigure(1, weight=1)

# Add Treeview for files
file_columns = ("Name", "Size", "Modified")
file_tree = ttk.Treeview(frame_file_list, columns=file_columns, show='headings')

# Define column headings
file_tree.heading('Name', text='Name')
file_tree.heading('Size', text='Size')
file_tree.heading('Modified', text='Modified')

# Configure column widths
file_tree.column('Name', width=300)
file_tree.column('Size', width=100, anchor='e')  # 'e' for east/right alignment
file_tree.column('Modified', width=150)

# Add scrollbars for file tree
file_vsb = ttk.Scrollbar(frame_file_list, orient="vertical", command=file_tree.yview)
file_hsb = ttk.Scrollbar(frame_file_list, orient="horizontal", command=file_tree.xview)
file_tree.configure(yscrollcommand=file_vsb.set, xscrollcommand=file_hsb.set)

# Grid layout for treeview and scrollbars
file_tree.grid(row=0, column=0, sticky=tk.NSEW)
file_vsb.grid(row=0, column=1, sticky=tk.NS)
file_hsb.grid(row=1, column=0, sticky=tk.EW)

# Add file count label
lbl_file_count = ttk.Label(frame_file_list, text="Files: 0")
lbl_file_count.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5)

# Add button frame below treeview
frame_file_buttons = ttk.Frame(frame_file_list)
frame_file_buttons.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.EW)

# Add "Add New Songs to DB" button
frame_file_format = ttk.Frame(frame_file_buttons)
frame_file_format.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)

ttk.Label(frame_file_buttons, text="Filename Format:").pack(side=tk.LEFT, padx=5)
filename_format = ttk.Combobox(frame_file_buttons, values=["Artist - Title", "Title - Artist"], state="readonly", width=20)
filename_format.pack(side=tk.LEFT, padx=3)
filename_format.set("Artist - Title")  # Set default value

btn_add_to_db = ttk.Button(frame_file_buttons, text="Add New Songs to DB", command=lambda: add_songs_to_db())
btn_add_to_db.pack(side=tk.TOP, anchor=tk.CENTER)

frame_file_list.grid_rowconfigure(0, weight=1)
frame_file_list.grid_columnconfigure(0, weight=1)

def show_file_context_menu(event):
    """Show the context menu on right click."""
    item = file_tree.identify_row(event.y)
    if item:
        file_tree.selection_set(item)
        file_context_menu.post(event.x_root, event.y_root)

def rename_selected_file():
    """Rename the selected file in the treeview."""
    if not file_tree.selection():
        return
        
    item = file_tree.selection()[0]
    old_filename = file_tree.item(item)['values'][0]
    folder_path = txt_folder.get()
    old_filepath = os.path.join(folder_path, old_filename)
    
    # Show rename dialog
    dialog = DialogFileRename(root, old_filename)
    root.wait_window(dialog.dialog)
    
    # If user clicked Save and provided a new name
    if dialog.result and dialog.result != old_filename:
        try:
            new_filepath = os.path.join(folder_path, dialog.result)
            
            # Check if target file already exists
            if os.path.exists(new_filepath):
                if not messagebox.askyesno("File Exists", 
                    f"File '{dialog.result}' already exists. Do you want to overwrite it?"):
                    return
            
            # Rename the file
            os.rename(old_filepath, new_filepath)
            
            # Update the treeview
            stats = os.stat(new_filepath)
            size = f"{stats.st_size / 1024 / 1024:.2f} MB"
            modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
            
            file_tree.item(item, values=(
                dialog.result,
                size,
                modified
            ), tags=(str(stats.st_size), str(stats.st_mtime)))
            
            insertLog(f"Renamed '{old_filename}' to '{dialog.result}'")
            
        except OSError as e:
            error_msg = f"Error renaming file: {str(e)}"
            insertLog(error_msg)
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            insertLog(error_msg)
            messagebox.showerror("Error", error_msg)

def open_selected_file():
    """Open the selected file using the default system application."""
    if not file_tree.selection():
        return
        
    item = file_tree.selection()[0]
    filename = file_tree.item(item)['values'][0]
    folder_path = txt_folder.get()
    filepath = os.path.join(folder_path, filename)
    
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", filepath])
        elif sys.platform == "win32":  # Windows
            os.startfile(filepath)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["xdg-open", filepath])
        else:
            insertLog("Unsupported operating system for opening files.")
    except Exception as e:
        error_msg = f"Error opening file: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)

def delete_selected_file():
    """Delete the selected file from the filesystem."""
    if not file_tree.selection():
        return
        
    item = file_tree.selection()[0]
    filename = file_tree.item(item)['values'][0]
    folder_path = txt_folder.get()
    filepath = os.path.join(folder_path, filename)
    
    # Show confirmation dialog
    if not messagebox.askyesno("Confirm Delete", 
        f"Are you sure you want to delete this file?\n\n{filename}"):
        return
    
    try:
        # Delete the file
        os.remove(filepath)
        
        # Remove from treeview
        file_tree.delete(item)
        
        insertLog(f"Deleted file '{filename}'")
        
    except OSError as e:
        error_msg = f"Error deleting file: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)

# Create context menu for file management
file_context_menu = tk.Menu(file_tree, tearoff=0)
file_context_menu.add_command(label="Preview", command=preview_video)
file_context_menu.add_command(label="Open", command=open_selected_file)
file_context_menu.add_command(label="Rename", command=rename_selected_file)
file_context_menu.add_separator()
file_context_menu.add_command(label="Delete", command=delete_selected_file)

# Bind right-click event to show context menu
file_tree.bind('<Button-3>', show_file_context_menu)  # For Windows/Linux
file_tree.bind('<Button-2>', show_file_context_menu)  # For macOS

class DialogFileRename:
    def __init__(self, parent, old_filename):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Rename File")
        self.dialog.transient(parent)  # Make dialog modal
        self.dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on the parent window
        window_width = 400
        window_height = 120
        screen_width = parent.winfo_x() + parent.winfo_width()//2
        screen_height = parent.winfo_y() + parent.winfo_height()//2
        x = screen_width - window_width//2
        y = screen_height - window_height//2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create and pack the widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Add filename entry
        ttk.Label(frame, text="New filename:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_filename = ttk.Entry(frame, width=50)
        self.entry_filename.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        self.entry_filename.insert(0, old_filename)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        # Store the result
        self.result = None
        
    def save(self):
        """Save the new filename and close the dialog."""
        self.result = self.entry_filename.get()
        self.dialog.destroy()
        
    def cancel(self):
        """Cancel the rename operation."""
        self.dialog.destroy()

def sort_treeview(col):
    """Sort treeview when a column header is clicked."""
    # Get all items in the treeview
    items = [(file_tree.set(item, col), item) for item in file_tree.get_children('')]
    
    # Determine sort order
    reverse = False
    if hasattr(file_tree, '_sort_col') and file_tree._sort_col == col:
        reverse = not file_tree._sort_reverse
    file_tree._sort_col = col
    file_tree._sort_reverse = reverse
    
    # Sort items based on column
    if col == 'Size':
        # Sort by actual size in bytes (stored in tags)
        items = [(float(file_tree.item(item)['tags'][0]), item) for item in file_tree.get_children('')]
    elif col == 'Modified':
        # Sort by timestamp (stored in tags)
        items = [(float(file_tree.item(item)['tags'][1]), item) for item in file_tree.get_children('')]
    else:
        # Sort by string value for name
        items = [(file_tree.set(item, col).lower(), item) for item in file_tree.get_children('')]
    
    # Sort the items
    items.sort(reverse=reverse)
    
    # Move items in the sorted order
    for idx, (val, item) in enumerate(items):
        file_tree.move(item, '', idx)
    
    # Update column header
    for header in ['Name', 'Size', 'Modified']:
        if header == col:
            file_tree.heading(header, text=f"{header} {'↓' if reverse else '↑'}")
        else:
            file_tree.heading(header, text=header)

# Bind column headers to sorting function
file_tree.heading('Name', text='Name', command=lambda: sort_treeview('Name'))
file_tree.heading('Size', text='Size', command=lambda: sort_treeview('Size'))
file_tree.heading('Modified', text='Modified', command=lambda: sort_treeview('Modified'))

# Initial file list population
refresh_file_list()

# Add DB Management tab contents
# Create search frame for database query
frame_search = ttk.Frame(tab_db_management)
frame_search.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
tab_db_management.grid_columnconfigure(0, weight=1)

# Add search controls
lbl_search = ttk.Label(frame_search, text="Search Query:")
lbl_search.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

txt_search = ttk.Entry(frame_search)
txt_search.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
frame_search.grid_columnconfigure(1, weight=1)

# Bind Enter key to search function
txt_search.bind('<Return>', lambda event: search_database())

btn_search = ttk.Button(frame_search, text="Search", command=search_database)
btn_search.grid(row=0, column=2, padx=5, pady=5)

# Create frame for results
frame_results = ttk.Frame(tab_db_management)
frame_results.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
tab_db_management.grid_rowconfigure(1, weight=1)

# Add Treeview for results
# Update the columns tuple to include StartTime
columns = ("ID", "Artist", "Title", "Filepath", "StartTime")
tree = ttk.Treeview(frame_results, columns=columns, show='headings')

# Define column headings
tree.heading('ID', text='ID')
tree.heading('Artist', text='Artist')
tree.heading('Title', text='Title')
tree.heading('Filepath', text='Filepath')
tree.heading('StartTime', text='StartTime')

# Configure column widths
tree.column('ID', width=0, stretch=False, minwidth=0)  # Hide ID column
tree.column('Artist', width=200)
tree.column('Title', width=300)
tree.column('Filepath', width=300)
tree.column('StartTime', width=0, stretch=False, minwidth=0)  # Hide StartTime column

# Add scrollbars
vsb = ttk.Scrollbar(frame_results, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(frame_results, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Grid layout for treeview and scrollbars
tree.grid(row=0, column=0, sticky=tk.NSEW)
vsb.grid(row=0, column=1, sticky=tk.NS)
hsb.grid(row=1, column=0, sticky=tk.EW)

frame_results.grid_rowconfigure(0, weight=1)
frame_results.grid_columnconfigure(0, weight=1)

# Create context menu for database management
db_context_menu = tk.Menu(tree, tearoff=0)
db_context_menu.add_command(label="Preview", command=lambda: preview_video(tree.item(tree.selection()[0])['values'][3] if tree.selection() else ""))
db_context_menu.add_command(label="Edit", command=edit_song_details)
db_context_menu.add_separator()
db_context_menu.add_command(label="Delete", command=delete_song)

# Bind right-click event to show context menu
tree.bind('<Button-3>', show_db_context_menu)  # For Windows/Linux
tree.bind('<Button-2>', show_db_context_menu)  # For macOS

# Bind double-click event to show edit dialog
tree.bind('<Double-1>', lambda event: edit_song_details())

# Create frame for database management buttons
frame_db_buttons = ttk.Frame(tab_db_management)
frame_db_buttons.grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)

# Add buttons with equal spacing
frame_db_buttons.grid_columnconfigure(0, weight=0)  # Changed from 1 to 0 to keep checkbox left-aligned
frame_db_buttons.grid_columnconfigure(5, weight=0)  # Right spacing

# Add production checkbox
production_var = tk.BooleanVar()
chk_production = ttk.Checkbutton(frame_db_buttons, text="Production", variable=production_var)
chk_production.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

# Add Config button to frame_db_buttons
btn_config = ttk.Button(frame_db_buttons, text="Config", command=open_config_dialog)
btn_config.grid(row=0, column=1, padx=5, pady=5)

# Download DB button
btn_download_db = ttk.Button(frame_db_buttons, text="Download DB", command=lambda: download_database())
btn_download_db.grid(row=0, column=2, padx=5, pady=5)

# Add Upload DB button
btn_upload_db = ttk.Button(frame_db_buttons, text="Upload DB", command=lambda: upload_database())
btn_upload_db.grid(row=0, column=3, padx=5, pady=5)

# Add Verify button
btn_verify = ttk.Button(frame_db_buttons, text="Verify", command=lambda: verify_filepaths())
btn_verify.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

# Add "Null Entries" button
btn_null_entries = ttk.Button(frame_db_buttons, text="Null Entries", command=lambda: find_null_entries())
btn_null_entries.grid(row=0, column=5, padx=5, pady=5, sticky=tk.E)

def find_null_entries():
    """Query the database for songs with missing artist or title entries."""
    try:
        # Clear existing items in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Connect to the database
        db_path = get_db_path()
        if not os.path.exists(db_path):
            messagebox.showerror("Error", "Database file not found. Please download the database first.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query for entries with NULL or empty artist or title
        cursor.execute("""
            SELECT songid, artist, title, path 
            FROM dbsongs 
            WHERE artist IS NULL OR artist = '' OR title IS NULL OR title = ''
        """)

        # Add results to the treeview
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

        conn.close()

        # Show message if no results found
        if not tree.get_children():
            messagebox.showinfo("Search Results", "No songs with missing artist or title found.")
        else:
            messagebox.showinfo("Search Results", "Songs with missing artist or title have been listed.")

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error querying database: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

def verify_filepaths():
    """Verify if the file paths for each row in the database exist."""
    try:
        # Connect to the database
        db_path = get_db_path()
        if not os.path.exists(db_path):
            messagebox.showerror("Error", "Database file not found. Please download the database first.")
            return

        # Clear existing items in the treeview
        for item in tree.get_children():
            tree.delete(item)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all rows from the database
        cursor.execute("SELECT songid, artist, title, path FROM dbsongs")
        rows = cursor.fetchall()

        missing_files = []
        for row in rows:
            songid, artist, title, filepath = row
            if not os.path.exists(filepath):
                missing_files.append((songid, artist, title, filepath))

        conn.close()

        # Display results
        if missing_files:
            messagebox.showwarning(
                "Missing Files",
                f"{len(missing_files)} file(s) are missing. Check the logs for details."
            )
            for songid, artist, title, filepath in missing_files:
                insertLog(f"Missing: {artist} - {title} [{filepath}]")
                tree.insert('', 'end', values=(songid, artist, title, filepath))
        else:
            messagebox.showinfo("Verification Complete", "All file paths are valid.")

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error verifying file paths: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

class DialogSongEdit:
    def __init__(self, parent, old_artist, old_title, old_filepath, old_starttime):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Song Details")
        self.dialog.transient(parent)  # Make dialog modal
        self.dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on the parent window
        window_width = 500
        window_height = 210
        screen_width = parent.winfo_x() + parent.winfo_width()//2
        screen_height = parent.winfo_y() + parent.winfo_height()//2
        x = screen_width - window_width//2
        y = screen_height - window_height//2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create and pack the widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Add entry fields
        ttk.Label(frame, text="Artist:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_artist = ttk.Entry(frame, width=50)
        self.entry_artist.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        self.entry_artist.insert(0, old_artist)
        
        ttk.Label(frame, text="Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_title = ttk.Entry(frame, width=50)
        self.entry_title.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        self.entry_title.insert(0, old_title)
        
        ttk.Label(frame, text="Filepath:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_filepath = ttk.Entry(frame, width=50)
        self.entry_filepath.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        self.entry_filepath.insert(0, old_filepath)
        # Scroll to the end of filepath to show filename
        self.entry_filepath.xview_moveto(1)
        
        # Add Start Time field
        ttk.Label(frame, text="Start Time:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_start_time = ttk.Entry(frame, width=50)
        self.entry_start_time.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        self.entry_start_time.insert(0, old_starttime)  # Default value
        
        # Buttons (update row number from 3 to 4)
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Fix Case", command=self.fix_case).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Save", command=self.save).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        # Bind ESC key to close dialog
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Store the result
        self.result = None
        
    def fix_case(self):
        """Apply title case to artist and title fields."""
        artist = self.entry_artist.get()
        title = self.entry_title.get()
        
        # Update the entry fields with title-cased text
        self.entry_artist.delete(0, tk.END)
        self.entry_artist.insert(0, to_title_case(artist))
        
        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, to_title_case(title))
        
    def save(self):
        """Save the edited details and close the dialog."""
        self.result = {
            'artist': self.entry_artist.get(),
            'title': self.entry_title.get(),
            'filepath': self.entry_filepath.get(),
            'start_time': self.entry_start_time.get()
        }
        self.dialog.destroy()
        
    def cancel(self):
        """Cancel the edit operation."""
        self.dialog.destroy()

class DialogVideoPreview:
    def __init__(self, parent, video_path):
        # Initialize audio_loaded flag first
        self.audio_loaded = False
        
        # Initialize pygame with a different audio backend
        pygame.init()
        pygame.mixer.quit()  # Reset the mixer
        
        # Try different audio initialization settings
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        except pygame.error:
            try:
                # Try alternative settings if the first attempt fails
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=2048)
            except pygame.error as e:
                print(f"Could not initialize audio: {e}")
                messagebox.showwarning("Audio Warning", "Audio playback may not be available.")
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Video Preview")
        self.dialog.transient(parent)
        
        # Set minimum initial size
        self.dialog.minsize(640, 480)
        
        # Set initial window size
        window_width = 800
        window_height = 600
        
        # Center the dialog on the parent window
        screen_width = parent.winfo_x() + parent.winfo_width()//2
        screen_height = parent.winfo_y() + parent.winfo_height()//2
        x = screen_width - window_width//2
        y = screen_height - window_height//2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create video display canvas
        self.canvas = tk.Canvas(self.dialog, bg='black')
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Create control buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_play = ttk.Button(btn_frame, text="Play", command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        # Add volume slider
        ttk.Label(btn_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_scale = ttk.Scale(btn_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                    command=self.update_volume)
        self.volume_scale.set(50)  # Set default volume to 50%
        self.volume_scale.pack(side=tk.LEFT, padx=5)
        
        self.btn_close = ttk.Button(btn_frame, text="Close", command=self.close)
        self.btn_close.pack(side=tk.RIGHT, padx=5)
        
        # Video handling
        self.video_path = video_path
        self.is_playing = False
        self.after_id = None
        self.first_play = True
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(video_path)
        if self.cap.isOpened():
            # Get video properties
            self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
            self.frame_delay = int(1000 / self.frame_rate)  # Convert to milliseconds
            
            try:
                # Try to load audio
                pygame.mixer.music.load(video_path)
                pygame.mixer.music.set_volume(0.5)  # Set initial volume to 50%
                self.audio_loaded = True
                print("Audio loaded successfully")
            except Exception as e:
                print(f"Error loading audio: {e}")
                self.audio_loaded = False
                messagebox.showwarning("Audio Warning", 
                    "Could not load audio. Video will play without sound.")
        
        # Show first frame
        self.show_frame()
        
        # Bind close event
        self.dialog.protocol("WM_DELETE_WINDOW", self.close)
        
        # Bind resize event
        self.canvas.bind('<Configure>', self.on_resize)
    
    def on_resize(self, event):
        """Handle window resize events."""
        if hasattr(self, 'current_frame'):
            self.update_frame_display(self.current_frame)
    
    def update_frame_display(self, frame):
        """Update the displayed frame with proper scaling."""
        if frame is None:
            return
            
        # Get current canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Check for valid canvas dimensions
        if canvas_width <= 0 or canvas_height <= 0:
            return
            
        # Get frame dimensions
        frame_height, frame_width = frame.shape[:2]
        
        # Calculate scaling factor
        width_scale = canvas_width / frame_width
        height_scale = canvas_height / frame_height
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        new_width = max(int(frame_width * scale), 1)
        new_height = max(int(frame_height * scale), 1)
        
        try:
            # Resize frame
            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert frame from BGR to RGB
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)
            
            # Calculate position to center the frame
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(x, y, image=photo, anchor=tk.NW)
            self.canvas.image = photo  # Keep a reference
            
        except cv2.error as e:
            print(f"OpenCV error during frame resize: {e}")
        except Exception as e:
            print(f"Error updating frame display: {e}")
    
    def show_frame(self):
        """Display the current video frame."""
        if not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.update_frame_display(frame)
            
            if self.is_playing:
                self.after_id = self.dialog.after(self.frame_delay, self.show_frame)
        else:
            # Reset video to start when it reaches the end
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if self.is_playing:
                if self.audio_loaded:
                    try:
                        pygame.mixer.music.play()
                    except pygame.error as e:
                        print(f"Error restarting audio: {e}")
                        self.audio_loaded = False
                self.show_frame()
    
    def toggle_play(self):
        """Toggle between play and pause."""
        self.is_playing = not self.is_playing
        self.btn_play.configure(text="Pause" if self.is_playing else "Play")
        
        if self.is_playing:
            if self.audio_loaded:
                if self.first_play:
                    try:
                        pygame.mixer.music.play()
                        self.first_play = False
                    except pygame.error as e:
                        print(f"Error playing audio: {e}")
                        self.audio_loaded = False
                else:
                    try:
                        pygame.mixer.music.unpause()
                    except pygame.error as e:
                        print(f"Error unpausing audio: {e}")
                        self.audio_loaded = False
            self.show_frame()
        else:
            if self.audio_loaded:
                try:
                    pygame.mixer.music.pause()
                except pygame.error as e:
                    print(f"Error pausing audio: {e}")
                    self.audio_loaded = False
            if self.after_id:
                self.dialog.after_cancel(self.after_id)
    
    def update_volume(self, value):
        """Update the audio volume."""
        if self.audio_loaded:
            try:
                volume = float(value) / 100
                pygame.mixer.music.set_volume(volume)
            except pygame.error as e:
                print(f"Error updating volume: {e}")
                self.audio_loaded = False
    
    def close(self):
        """Clean up resources and close the dialog."""
        if self.after_id:
            self.dialog.after_cancel(self.after_id)
        if self.cap.isOpened():
            self.cap.release()
        if self.audio_loaded:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except pygame.error as e:
                print(f"Error cleaning up audio: {e}")
        pygame.quit()
        self.dialog.destroy()


def preview_video(fname=""):
    
    filepath = fname
    if fname == "":    
        """Open video preview dialog for the selected file."""
        if not file_tree.selection():
            return
            
        item = file_tree.selection()[0]
        filename = file_tree.item(item)['values'][0]
        folder_path = txt_folder.get()
        filepath = os.path.join(folder_path, filename)
    
    if not filepath.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
        messagebox.showwarning("Warning", "Selected file is not a video file.")
        return
    
    if not os.path.exists(filepath):
        messagebox.showerror("Error", f"File not found: {filepath}")
        return
    
    try:
        # dialog = DialogVideoPreview(root, filepath)
        
        # Determine preview script path
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle (extract path)
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)        
        
        # preview_bin = os.path.join(base_path, 'preview_player')
        preview_bin = os.path.join(base_path, 'preview_player', 'preview_player')

        preview_player_path = os.path.join(base_path, 'preview_player.py')
        
        # Use system python to run preview_player.py
        python_path = shutil.which("python3") or shutil.which("python")

        if python_path is None:
            messagebox.showerror("Error", "Python interpreter not found.")
            return        
        
        # preview_player_path = os.path.join(os.path.dirname(__file__), 'preview_player.py')
        # python3_path = config.get('PATHS', 'PYTHON3_PATH', fallback='python3') 

        # if python_path == '':
        #     insertLog("PYTHON3_PATH not set in config.ini")
        #     python_path = 'python3'
            
        # subprocess.Popen([sys.executable, preview_player_path, filepath])
        process = subprocess.Popen([python_path, preview_player_path, filepath], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        
        # Assume preview_player is next to the .app bundle
        # main_app_dir = Path(sys.executable).parent.parent.parent  # Mac .app path: Contents/MacOS/...
        # preview_bin = main_app_dir / "preview_player" / "preview_player"

        
        # process = subprocess.Popen([str(preview_bin), filepath], 
        #                   stdout=subprocess.PIPE, 
        #                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        insertLog(f"Output: {stdout.decode()}")
        insertLog(f"Error: {stderr.decode()}")
        
    except Exception as e:
        error_msg = f"Error previewing video: {str(e)}"
        insertLog(error_msg)
        messagebox.showerror("Error", error_msg)

class DialogProcessing:
    def __init__(self, parent, title="Processing", message="Please wait..."):
        """Initialize the processing dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)  # Make it modal
        self.dialog.grab_set()  # Prevent interaction with the main window

        # Center the dialog on the parent window
        window_width = 300
        window_height = 120
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Add a label to indicate processing
        self.label = ttk.Label(self.dialog, text=message)
        self.label.pack(pady=5)

        # Add a spinner progress below the text
        self.spinner = ttk.Progressbar(self.dialog, mode='indeterminate', length=200)
        self.spinner.pack(pady=5)
        self.spinner.start(20)  # Start the spinner animation with a faster interval (10ms)

        # Add a close button (disabled by default)
        self.close_button = ttk.Button(self.dialog, text="Close", command=self.close, state=tk.DISABLED)
        self.close_button.pack(pady=5)

    def update_message(self, new_message, playsound):
        """Update the displayed message."""
        self.label.config(text=new_message)
        
        if playsound != "":
            play_sound(playsound)

    def toggle_close_button(self, enable=True):
        """Enable or disable the close button."""
        state = tk.NORMAL if enable else tk.DISABLED
        self.close_button.config(state=state)
        self.spinner.stop()  # Stop the spinner animation
        self.spinner.config(mode='determinate', value=100)  # Set progress to 100%

    def close(self):
        """Close the processing dialog."""
        self.dialog.destroy()

root.resizable(width=True, height=True)
root.geometry("700x600")

# Center the window on the screen
window_width = 750
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Start the keyboard listener in a separate thread
# keyboard_listener_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
# keyboard_listener_thread.start()

def on_closing():
    global keyboard_listener
    # Signal the listener to stop
    print("Closing application")
    stop_event.set()
    if keyboard_listener:
        print("Stopping keyboard listener")
        keyboard_listener.stop()
    root.destroy()
    
root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the application
root.mainloop()
