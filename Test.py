import ffmpeg

def get_video_duration(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        duration_seconds = float(probe['format']['duration'])
        return duration_seconds
    except Exception as e:
        print(f"Error probing video: {e}")
        return None

video_file = "/Users/guyjasper/Documents/Guy/Projects/Python/DownloadYT/NEW_SONGS/At Seventeen - Janis Ian.mp4"  # Replace with your video file path
duration = get_video_duration(video_file)

if duration is not None:
    print(f"Duration: {int( duration*1000)} milliseconds")
    minutes, seconds = divmod(int(duration), 60)
    print(f"Duration: {minutes:02}:{seconds:02} (mm:ss)")
else:
    print("Could not retrieve duration.")
