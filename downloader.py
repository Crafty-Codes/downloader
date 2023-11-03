import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import os

# Function to get the HTML content from a URL
def get_html(url):
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.text
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        return None

# Function to find the href preceding the specific <i> tag
def find_preceding_href(html):
    soup = BeautifulSoup(html, 'html.parser')
    icon_tag = soup.find('i', class_="icon Vidoza")
    if icon_tag:
        prev_tag = icon_tag.find_previous('a', class_="watchEpisode")
        if prev_tag:
            return prev_tag.get('href')
    return None

# Function to find the video src attribute from the downloaded HTML
def find_video_src(html):
    soup = BeautifulSoup(html, 'html.parser')
    video_tag = soup.find('video')
    if video_tag:
    #     return video_tag.get('src')
    # else:
        # If the <video> tag does not have src, check for <source> inside it
        source_tag = soup.find('source')
        if source_tag:
            return source_tag.get('src')
    return None

# Get the initial HTML content
def get_video_link(url):
    initial_html = get_html(url)
    if initial_html:
        # Find the preceding href
        preceding_href = find_preceding_href(initial_html)
        if preceding_href:
            full_url = urljoin(url, preceding_href)
            print(f"Following link to: {full_url}")

                # Get the HTML content of the new page
            second_html = get_html(full_url)
            if second_html:
            # Find the video src
                video_src = find_video_src(second_html)
                if video_src:
                    return video_src
                    # print(f"Video src found: {video_src}")
                        # Here you can add your code to download the video or do something with the video URL
                else:
                    print("Video src not found in the new page.")
        else:
            print("No preceding href found.")

    return ""
# Base URL pattern
base_url_pattern = "https://s.to/serie/stream/steel-buddies/staffel-{staffel}/episode-{episode}"

# Headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Initial staffel and episode
staffel = 1
episode = 1

while True:
    # Construct URL
    url = base_url_pattern.format(staffel=staffel, episode=episode)
    # Make a request to the constructed URL
    response = requests.get(url, headers=headers)

    # If the request is successful, print the URL and increment the episode number
    if response.status_code == 200 and len(response.text) != 0:
        print(f"Valid URL: {url}")
        video_url = get_video_link(url)

        output = f"steel-buddies/season-{staffel}"

        if not os.path.exists(output):
            # Create a new directory because it does not exist
            os.makedirs(output)

        output_path = output + f"/episode-{episode}.mp4"

        # Stream the video content in chunks
        response = requests.get(video_url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the total file size
            file_size = int(response.headers.get('content-length', 0))

            # Progress bar setup
            progress = tqdm(response.iter_content(1024), f"Downloading {output_path}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)

            # Open the output file and write the content in chunks
            with open(output_path, 'wb') as f:
                for data in progress:
                    # Write data read to the file
                    f.write(data)
                    # Update the progress bar manually
                    progress.update(len(data))
            progress.close()
        else:
            print(f"Error occurred while downloading the file. Status Code: {response.status_code}")

        episode += 1
    else:
        # If the episode does not exist, reset episode to 1 and increment staffel
        episode = 1
        staffel += 1
        # Check the next season's first episode to see if it exists
        new_season_url = base_url_pattern.format(staffel=staffel, episode=episode)
        response = requests.get(new_season_url, headers=headers)

        # If the new season's first episode does not exist, break the loop
        if staffel >= 12:
            print(f"Season {staffel} does not exist. Stopping iteration.")
            break
        else:
            print()
            # print(f"Starting new season: {new_season_url}")

# Final message
print("Finished iterating through all seasons and episodes.")
