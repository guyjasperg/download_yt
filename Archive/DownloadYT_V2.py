from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import os
import time
import subprocess
from UtilityFunctions import *

basse_url = 'https://www.youtube.com/watch?v='
video_id = 'HNy41EFCJcs'

RAW_FOLDER = "DOWNLOADS/"

video_filename = ""
audio_filename = ""

yt = None

def time_function(func):
  """
  Decorator to measure the execution time of a function.

  Args:
    func: The function to be timed.

  Returns:
    A wrapper function that measures and prints the execution time.
  """
  def wrapper(*args, **kwargs):
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Function {func.__name__} executed in {elapsed_time:.4f} seconds.")
    return result
  return wrapper

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
  print(f"\rDownloaded: {bytes_downloaded / 1024 / 1024:.2f}MB / {total_size / 1024 / 1024:.2f}MB ({percentage_of_completion:.2f}%)", end="")

def is_playlist_url(url):
  """
  Checks if the given URL is a YouTube playlist URL.

  Args:
    url: The URL to check.

  Returns:
    True if the URL is a playlist URL, False otherwise.
  """
  try:
    Playlist(url)  # Attempt to create a Playlist object
    return True
  except Exception: 
    try:
      YouTube(url)  # Attempt to create a YouTube object (for single videos)
      return False
    except Exception:
      return False  # Handle cases where neither Playlist nor YouTube object can be created

#@time_function
def get_playlist_video_titles(playlist_url):
    """
    Fetches and prints video titles from a YouTube playlist URL.

    Args:
        playlist_url: The URL of the YouTube playlist.

    Returns:
        A list of video titles.
    """

    try:
        playlist = Playlist(playlist_url)
        video_titles = []

        for video in playlist.videos:
            video_titles.append(video.title)

        return video_titles

    except Exception as e:
        print(f"Error: Invalid playlist URL: {e}")
        return []

    # except Exception.VideoUnavailable:
    #     print(f"Error: Some videos in the playlist may be unavailable.")
    #     return video_titles  # Continue with available titles

    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    #     return []

#Function definitions
def Downloadfiles(videostream, audiostream):
    print(f"Downloadfiles({videostream.title})")
    global video_filename
    global audio_filename
    global yt

    try:        
        if videostream:
            #title = CleanFilename(videostream.default_filename)
            print(f"[{video_filename}]")
            ys = yt.streams.get_by_itag(videostream.itag)
            ys.download(filename=f"{RAW_FOLDER}{video_filename}")

        if audiostream:
            #title = audiostream.default_filename
            print(f"\n[{audio_filename}]")
            ys = yt.streams.get_by_itag(audiostream.itag)
            ys.download(filename=f"{RAW_FOLDER}{audio_filename}")

        return True
    except Exception as e:
        print(f"An error occurred downloading files. [{e}]")
        return False
#remove invalid characters from file name
def CleanFilename(filename):
    #TBD
    return str(filename).replace('/',' ')

MERGE_FILES = True

user_input = "start"

#MAIN LOOP
def main():
    global user_input
    global video_filename
    global audio_filename
    global yt

    while user_input.lower() != "exit":
        print("Enter Video ID to download:")
        user_input = input()

        if user_input == "":
            print("Invalid input!")
            continue

        if(user_input.lower() == 'exit'):
            break

        #Process video
        url = f"{basse_url}{user_input}"
        url = user_input

        #check if url is a playlist
        # if is_playlist_url(url):
        #     print("Getting playlist video titles...")
        #     titles = get_playlist_video_titles(url)
        #     titles.sort()
        #     for title in titles:
        #         print(f"{remove_keywords(CleanFilename(title))}")
        #     continue

        try:
            print("\ncontacting server...")
            # yt = YouTube(url, on_progress_callback=on_progress)
            # yt = YouTube(url, on_progress_callback=on_progress, use_po_token=True)
            yt = YouTube(url,'WEB', on_progress_callback=on_progress )

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

        _title = CleanFilename(yt.title)
        print(f"{_title}\n")

        selectedVideoStream = None

        #select highest resolution video
        # Sort streams by resolution in descending order
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
            #print(selectedVideoStream.default_filename)
            video_filename = f"{remove_keywords(CleanFilename(selectedVideoStream.default_filename),"")}"
            print(f"selected video stream: [{selectedVideoStream.itag}] {selectedVideoStream.resolution}")
            if selectedVideoStream.includes_audio_track == False:
                print("No audio track")
        else:
            print("No video stream selected.")

        selectedAudioStream = None

        #if stream has no audio, select audio stream
        if selectedVideoStream.includes_audio_track == False:
            print("searching audio track")
            #select audio
            for stream1 in yt.streams.filter(type="audio"):
                #filter only for mp4
                if(stream1.abr == '128kbps'):
                    selectedAudioStream = stream1

        audio_filename = ""
        if selectedAudioStream != None:
            #print(selectedAudioStream.default_filename)
            audio_filename = f"{remove_keywords(CleanFilename(selectedAudioStream.default_filename),"")}"
            print(f"selected audio stream: [{selectedAudioStream.itag}] {selectedAudioStream.abr}")
        else:
            print("No audio stream selected")

        print("\nDownloading files...")
        if Downloadfiles(selectedVideoStream, selectedAudioStream) == False:
            continue

        #If separate audio file, then merge
        if MERGE_FILES == True and selectedAudioStream != None:
            print("\n\nMerging audio and video streams...")

            # Combine video and audio using ffmpegexit
            
            output_dir = "/Volumes/KINGSTONSSD/_Karaoke/_NEW_SONGS/"
            
            # Check if the provided directory exists
            if not os.path.isdir(output_dir):
                #mobile drive not available, use local
                output_dir = "NEW_SONGS/"

            output_file = f"{output_dir}{video_filename}"

            if os.path.isfile(output_file):
                print("file already exists!")
                continue
            
            print(f"saving file to ->{output_file}")

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

        print("\n")
    # print("End.")

#call main function
if __name__ == "__main__":
    main()

print("End.")
