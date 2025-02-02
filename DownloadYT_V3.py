from pytubefix import YouTube, Playlist
from pytubefix.exceptions import VideoUnavailable, VideoPrivate, VideoRegionBlocked, AgeRestrictedError, RegexMatchError
import ffmpeg
import os
import re
#import sys

# Define a progress callback function for downloads
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    print(f"Downloading... {percentage:.2f}% complete")

# Function to sanitize the video title for use in filenames
def sanitize_filename(title):
    # Remove invalid characters for filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', "", title)  # Remove invalid characters
    sanitized = sanitized.strip()  # Remove leading/trailing spaces
    return sanitized

# Function to check if a file exists and prompt for overwrite
def check_overwrite(file_path):
    if os.path.exists(file_path):
        response = input(f"The file '{file_path}' already exists. Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("Operation canceled.")
            return False
    return True

# Function to parse FFmpeg progress from stderr
def parse_progress(line):
    # Regex to extract progress information from FFmpeg output
    regex = r"frame=\s*(\d+)\s+fps=\s*([\d.]+)\s+q=\s*([\d.-]+)\s+size=\s*(\d+)\w+\s+time=\s*([\d:.]+)\s+bitrate=\s*([\d.]+)\w+\/s\s+speed=\s*([\d.]+)x"
    match = re.search(regex, line)
    if match:
        frame, fps, q, size, time, bitrate, speed = match.groups()
        return {
            "frame": int(frame),
            "fps": float(fps),
            "q": float(q),
            "size": int(size),
            "time": time,
            "bitrate": float(bitrate),
            "speed": float(speed),
        }
    return None

# Function to merge video and audio using ffmpeg-python with progress monitoring
def merge_video_audio(video_file, audio_file, output_file):
    try:
        print("Merging video and audio using ffmpeg-python...")
        
        # Use ffmpeg-python to merge video and audio
        process = (
            ffmpeg
            .input(video_file)  # Input video file
            .output(ffmpeg.input(audio_file), output_file, vcodec='copy', acodec='aac', strict='experimental')
            .global_args("-progress", "pipe:1")  # Enable progress reporting
            .run_async(pipe_stdout=True, pipe_stderr=True)  # Run asynchronously and capture output
        )
        
        # Monitor progress
        while True:
            line = process.stderr.readline().decode("utf-8")
            if line == "" and process.poll() is not None:
                break  # Exit loop when process is complete
            
            # Parse and display progress
            progress = parse_progress(line)
            if progress:
                print(f"Progress: Time={progress['time']}, Speed={progress['speed']}x, Size={progress['size']}KB")
        
        # Wait for the process to complete
        process.wait()
        
        if process.returncode == 0:
            print("Merge completed successfully.")
        else:
            print(f"Merge failed. FFmpeg error code: {process.returncode}")
    except ffmpeg.Error as e:
        print(f"Merge failed. FFmpeg error: {e.stderr.decode('utf-8')}")
    except Exception as e:
        print(f"An error occurred during merging: {e}")

# Function to download a single video
def download_video(video_url):
    try:
        # Create a YouTube object
        yt = YouTube(video_url, on_progress_callback=on_progress)

        # Sanitize the video title for use in filenames
        sanitized_title = sanitize_filename(yt.title)

        # Get the highest resolution video stream
        #video_stream = yt.streams.filter(progressive=True, fileexit_extension='mp4').order_by('resolution').desc().first()
        video_stream = None
        for stream in yt.streams.filter(type="video"):
            if(stream.height >= 360 and stream.subtype == "mp4"):
                if(video_stream == None):
                    video_stream = stream
                else:
                    if(video_stream.height < stream.height):
                        video_stream = stream

        # Check if the video stream includes audio
        if video_stream.includes_audio_track:
            print(f"Video includes audio. Downloading video with audio: {yt.title}...")
            output_file = f"{sanitized_title} video with audio.mp4"
            if check_overwrite(output_file):
                video_stream.download(output_path=".", filename=output_file)
        else:
            print(f"Video does not include audio. Downloading video and audio separately: {yt.title}...")
            
            # Download video without audio
            video_file = f"{sanitized_title} video only.mp4"
            if check_overwrite(video_file):
                print("Downloading video...")
                video_stream.download(output_path=".", filename=video_file)
            
            # Download the best audio stream with at least 128 kbps bitrate
            audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            
            # Ensure the audio stream has at least 128 kbps bitrate
            if audio_stream and int(audio_stream.abr[:-4]) >= 128:  # abr is in the format "128kbps"
                audio_file = f"{sanitized_title} audio only.mp4"
                if check_overwrite(audio_file):
                    print(f"Downloading audio with {audio_stream.abr} bitrate...")
                    audio_stream.download(output_path=".", filename=audio_file)
                
                    # Merge video and audio using ffmpeg-python
                    output_file = f"{sanitized_title} merged video.mp4"
                    if check_overwrite(output_file):
                        merge_video_audio(video_file, audio_file, output_file)
                    else:
                        print("Merge operation canceled.")
                else:
                    print("Audio download canceled.")
            else:
                print("No audio stream with at least 128 kbps bitrate found.")
            
            print("Video and audio downloaded and merged.")

            #delete temp files
            os.remove(video_file)
            os.remove(audio_file)

    except VideoUnavailable:
        print(f"Error: The video at '{video_url}' is unavailable.")
    except VideoPrivate:
        print(f"Error: The video at '{video_url}' is private.")
    except VideoRegionBlocked:
        print(f"Error: The video at '{video_url}' is blocked in your region.")
    except AgeRestrictedError:
        print(f"Error: The video at '{video_url}' is age-restricted and cannot be downloaded.")
    except RegexMatchError:
        print(f"Error: The URL '{video_url}' is not a valid YouTube video URL.")
    except Exception as e:
        print(f"An unexpected error occurred while processing '{video_url}': {e}")

# Function to download all videos in a playlist
def download_playlist(playlist_url):
    try:
        # Create a Playlist object
        playlist = Playlist(playlist_url)

        print(f"Downloading playlist: {playlist.title}")
        print(f"Number of videos in playlist: {len(playlist.videos)}")

        # Iterate over all videos in the playlist
        for video in playlist.videos:
            try:
                print(f"\nDownloading video: {video.title}")
                download_video(video.watch_url)
            except Exception as e:
                print(f"Failed to download video: {video.title}. Error: {e}")
    except Exception as e:
        print(f"An error occurred while processing the playlist '{playlist_url}': {e}")

# Function to check if a URL is a playlist
def is_playlist(url):
    try:
        # Attempt to create a Playlist object
        playlist = Playlist(url)
        # If the playlist has at least one video, it's a valid playlist
        return len(playlist.video_urls) > 0
    except Exception:
        # If an exception occurs, it's not a playlist
        return False

# Main function with loop for repeated input
def main():
    while True:
        # Ask the user for a URL
        url = input("Enter the YouTube video or playlist URL (or type 'exit' to quit): ").strip()
        
        # Exit the loop if the user types 'exit'
        if url.lower() == 'exit':
            print("Exiting...")
            break
        
        # Process the URL
        if is_playlist(url):
            # If the URL is a playlist, download all videos
            download_playlist(url)
        else:
            # If the URL is a single video, download it
            download_video(url)
        
        print("\nDownload complete!\n")

#Global Vars
RAW_FOLDER = "DOWNLOADS/"
OUTPUT_FOLDER = "/Volumes/KINGSTONSSD/_Karaoke/_NEW_SONGS/"

# Start the program
if __name__ == "__main__":
    main()