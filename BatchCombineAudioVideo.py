import os
import subprocess

def combine_audio_video_batch(directory):
    """
    Batch process combining video and audio files in a directory.
    For each video file, find the corresponding audio file and combine them using ffmpeg.

    Args:
        directory (str): The directory containing the video and audio files to be processed.
    """
    try:
        # Iterate through the files in the specified directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Only process video files (you can adjust the file types if needed)
            if filename.endswith(('.mp4', '.mkv', '.avi')):
                video_file = file_path
                base_name = os.path.splitext(filename)[0]

                # Look for the corresponding audio file (assuming .mp3 or .aac)
                audio_file = None
                for ext in ['.m4a','.mp3', '.aac']:
                    potential_audio_file = os.path.join(directory, base_name + ext)
                    if os.path.exists(potential_audio_file):
                        audio_file = potential_audio_file
                        break

                if audio_file:
                    print(f"Combining {video_file} and {audio_file}...")

                    # Combine video and audio using ffmpeg
                    output_file = os.path.join(directory, base_name + "_with_audio.mp4")
                    command = [
                        'ffmpeg',
                        '-i', video_file,
                        '-i', audio_file,
                        '-c:v', 'copy',  # Copy video codec (no re-encoding)
                        '-c:a', 'aac',   # Use AAC codec for audio
                        '-strict', 'experimental',  # To ensure ffmpeg accepts the audio format
                        output_file
                    ]
                    subprocess.run(command, check=True)

                    # If successful, delete the original video and audio files (optional)
                    os.remove(video_file)
                    os.remove(audio_file)
                    print(f"Combined video and audio saved to: {output_file}")
                else:
                    print(f"No matching audio file found for {video_file}. Skipping...")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
directory_path = "/Users/guyjasper/Documents/Guy/Projects/Python/HelloWorld/DOWNLOADS"  # Replace with the path to your directory
combine_audio_video_batch(directory_path)
