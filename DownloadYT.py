from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy import VideoFileClip, AudioFileClip
import os

basse_url = 'https://www.youtube.com/watch?v='
video_id = 'Z2g0jlx2IcM'

#Function definitions
def Downloadfiles(videostream, audiostream):
    if videostream != None:
        #title = CleanFilename(videostream.default_filename)
        print(f"[{video_filename}]")
        ys = yt.streams.get_by_itag(videostream.itag)
        ys.download(filename=video_filename)

    if audiostream != None:
        #title = audiostream.default_filename
        print(f"[{audio_filename}]")
        ys = yt.streams.get_by_itag(audiostream.itag)
        ys.download(filename=audio_filename)

#remove invalid characters from file name
def CleanFilename(filename):
    #TBD
    return str(filename).replace('/',' ')

MERGE_FILES = False

url = f"{basse_url}{video_id}"
# yt = YouTube(url, on_progress_callback=on_progress,use_po_token=True)
yt = YouTube(url, 'WEB')

_title = CleanFilename(yt.title)
print(f"{_title}\n")

selectedVideoStream = None

#select highest resolution video
for stream in yt.streams.filter(type="video"):
    if(stream.height >= 360 and stream.subtype == "mp4"):
        if(selectedVideoStream == None):
            selectedVideoStream = stream
        else:
            if(selectedVideoStream.height < stream.height):
                selectedVideoStream = stream

video_filename = ""
if selectedVideoStream != None:
    #print(selectedVideoStream.default_filename)
    video_filename = CleanFilename(selectedVideoStream.default_filename)
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
    audio_filename = CleanFilename(selectedAudioStream.default_filename)
    print(f"selected audio stream: [{selectedAudioStream.itag}] {selectedAudioStream.abr}")
else:
    print("No audio stream selected")

print("\nDownloading files...")
Downloadfiles(selectedVideoStream, selectedAudioStream)

#If separate audio file, then merge
if MERGE_FILES == True and selectedAudioStream != None:
    print("\n\nMerging audio and video streams...")
    video_clip = VideoFileClip(video_filename)
    audio_clip = AudioFileClip(audio_filename)
    video_clip.audio = audio_clip
    video_clip.write_videofile(f"NEW_SONGS/{_title}_with_audio.mp4")

    #delete separate audio / video files
    print("deleting temp files...")
    os.remove(video_filename)
    os.remove(audio_filename)
    
print("Done.")
