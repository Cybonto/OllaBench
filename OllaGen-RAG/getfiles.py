import os
import re
import requests

# Function to extract links from text
def extract_links_from_text(text):
    # Regular expression to find URLs in text
    url_pattern = re.compile(r'https?://\S+')
    return re.findall(url_pattern, text)

# Function to download a file from a URL and save it locally
def download_file(url, save_folder):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(save_folder, os.path.basename(url))
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url} (Status code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

# Input: Text file name
text_file_name = input("Enter the name of the text file containing links: ")

# Input: Local folder to save downloaded files
save_folder = input("Enter the local folder to save downloaded files: ")

# Check if the save folder exists, if not, create it
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

try:
    with open(text_file_name, 'r', encoding="utf8") as file:
        text = file.read()
        links = extract_links_from_text(text)
        
        if len(links) > 0:
            for link in links:
                download_file(link, save_folder)
        else:
            print("No links found in the text file.")

except FileNotFoundError:
    print(f"File '{text_file_name}' not found.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
