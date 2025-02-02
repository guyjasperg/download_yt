import requests

def download_facebook_video(url):
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    #soup = BeautifulSoup(response.content, 'html.parser') 
    # ... (Extract the actual video URL from the HTML using BeautifulSoup) 
    # ... (e.g., by searching for specific HTML tags or attributes)
    print(response)
    print(response.text)

    #video_url = "extracted_video_url"  # Replace with the extracted URL

    #video_data = requests.get(video_url).content
    #print(video_data)

    # Save the video data to a file
    # with open("facebook_video.mp4", "wb") as f:
    #   f.write(video_data)

  except Exception as e:
    print(f"An error occurred: {e}")


if __name__ == "__main__":
    url = "https://www.facebook.com/watch?v=1529641814378747"
    download_facebook_video(url)