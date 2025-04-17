# python script.py qa_spacereserveservices_user

import sys
import os
import http.client
import json
from urllib.parse import urlparse

# Get the `name` parameter from the command-line arguments
if len(sys.argv) < 2:
    raise ValueError("Please provide the 'name' parameter as a command-line argument.")
dynamic_name = sys.argv[1]  # The first argument is the dynamic `name`

# Construct the URL dynamically
api_url = f"http://172.16.1.236:8081/service/rest/v1/search/assets?direction=desc&repository=Space-Reserve&format=maven2&group=Space-Reserve&name={dynamic_name}&version=1.0.0"

def fetch_url(url):
    """Fetch data from the given URL using built-in libraries."""
    parsed_url = urlparse(url)
    conn = http.client.HTTPConnection(parsed_url.hostname, parsed_url.port)
    conn.request("GET", parsed_url.path + "?" + parsed_url.query)
    response = conn.getresponse()
    if response.status != 200:
        raise Exception(f"Failed to fetch URL: {url} (Status: {response.status} {response.reason})")
    return response.read().decode()

def download_file(url, filename):
    """Download a file from the given URL using built-in libraries."""
    parsed_url = urlparse(url)
    conn = http.client.HTTPConnection(parsed_url.hostname, parsed_url.port)
    conn.request("GET", parsed_url.path + "?" + parsed_url.query)
    response = conn.getresponse()
    if response.status != 200:
        raise Exception(f"Failed to download file: {url} (Status: {response.status} {response.reason})")
    
    # Write the downloaded content to the file
    with open(filename, "wb") as file:
        file.write(response.read())

def download_latest_zip():
    try:
        print(f"Fetching data from URL: {api_url}")

        # Fetching data from the URL
        data = fetch_url(api_url)
        data = json.loads(data)

        # Filter for ZIP files
        zip_assets = [item for item in data['items'] if item['downloadUrl'].endswith('.zip')]
        if not zip_assets:
            raise Exception("No ZIP files found in the response.")

        # Sort ZIP files by the lastModified field in descending order (latest first)
        latest_zip_asset = sorted(
            zip_assets, 
            key=lambda x: x['lastModified'], 
            reverse=True
        )[0]

        download_url = latest_zip_asset['downloadUrl']  # URL to download the latest ZIP
        original_filename = os.path.basename(download_url)  # Extract filename from the URL

        # Use absolute paths to ensure renaming works
        original_filepath = os.path.abspath(original_filename)
        renamed_filename = "latest_build.zip"  # Define the new name for the file
        renamed_filepath = os.path.abspath(renamed_filename)

        print(f"Downloading the latest ZIP file: {original_filename} from {download_url}")

        # Download the ZIP file
        download_file(download_url, original_filepath)
        print(f"File downloaded successfully: {original_filepath}")

        # Verify the original file exists before renaming
        if not os.path.exists(original_filepath):
            raise Exception(f"Downloaded file not found: {original_filepath}")

        # Rename the downloaded file
        os.rename(original_filepath, renamed_filepath)
        print(f"File renamed successfully to: {renamed_filepath}")
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)

# Call the function to download and rename the latest ZIP file
download_latest_zip()