# Import ChromeOptions to set ChromeDriver options
from selenium.webdriver import Chrome, ChromeOptions
# Import By to determine the method of finding an element
from selenium.webdriver.common.by import By
# Import WebDriverWait to wait for a page to load
from selenium.webdriver.support.ui import WebDriverWait
# Import expected_conditions to determine if a page has loaded
from selenium.webdriver.support import expected_conditions as EC
# Import webdriver from selenium to use the ChromeDriver
from selenium import webdriver

import requests  # Import requests to get the HTML code of a page
import time     # Import time to add delays to the program
import io       # Import io to create a file stream
from pathlib import Path  # Import Path to check if a file exists
import hashlib  # Import hashlib to create a hash of a file
import pandas as pd  # Import pandas to create a DataFrame
import os  # Import os to remove a file
from datetime import datetime  # Import datetime to get the current time

from bs4 import BeautifulSoup  # Import BeautifulSoup to parse HTML
from PIL import Image  # Import Image from PIL to open and save images
from urllib.parse import urlparse

###############################################################################

# Store the content of a web page in a variable


def get_content_from_url(url):
    # Add "executable_path=" if the driver is in a custom directory.
    driver = webdriver.Chrome()  # Create a ChromeDriver instance
    driver.get(url)  # Open the URL
    # driver.maximize_window()  # Maximize the window

    scroll_to_bottom(driver)  # Scroll to the bottom of the page

    time.sleep(4)  # Wait for the page to load.
    # Get the HTML content of the page and store it in a variable.
    page_content = driver.page_source
    driver.quit()  # You don't need the browser instance for further steps.
    print("Got the content of the page successfully!")
    return page_content

###############################################################################

# Function to scroll to the bottom of the page


def scroll_to_bottom(driver):
    # Get the current height of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    target_time = time.time() + 8*60  # One hour from now

    # while time.time() < target_time:
    while True:
        # Calculate the remaining time
        time_difference = int(target_time - time.time())
        hours = time_difference // 3600
        minutes = (time_difference % 3600) // 60
        seconds = time_difference % 60

        # Display the remaining time
        # print(f"Countdown: {hours:02d}:{minutes:02d}:{seconds:02d}", end='\r')

        # Scroll down to the bottom of the page
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load
        time.sleep(2)

        # Click on the "Load more" button
        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "masonry-load-more-button")))
            element.click()
        except:
            print("No more images to load!")
            break

        # Get the new height of the page
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Check if the new height is equal to the last height
        if new_height == last_height:
            break

        # Set the last height to the new height
        last_height = new_height

    print("Scrolled to the bottom of the page successfully!")

###############################################################################

# Function to parse the image URLs from the HTML content


def parse_image_urls(content, classes, location, source):
    soup = BeautifulSoup(content, features="html.parser")
    results = []
    for a in soup.findAll(attrs={"class": classes}):
        name = a.find(location)
        if name not in results:
            results.append(name.get(source))
    print("Parsed all links successfully!")
    return results

###############################################################################

# Function to save the image URLs to a CSV file


def save_urls_to_csv(image_urls, filename):
    df = pd.DataFrame({"links": image_urls})
    df.to_csv(filename, index=False, encoding="utf-8")
    print("Saved all links to CSV file successfully!")

###############################################################################

# Function to download the image from the URL and save it to a file


def download_image_to_file(filename):
    df = pd.read_csv(filename)
    for index, row in df.iterrows():
        try:
            string = row[0]
            response = requests.get(string)
            image_bytes = io.BytesIO(response.content)
            image = Image.open(image_bytes)
            # create a folder to store the images
            pathname = "images_" + filename
            Path(pathname).mkdir(parents=True, exist_ok=True)
            image.save(f"{pathname}/" + str(index) + ".jpg")
        except:
            print("Error downloading image", index)
            continue
    print("Downloaded all images successfully!")
###############################################################################

# Function to store the links of images to a CSV file


def extract_link_csv(file):
    # Read the CSV file
    df = pd.read_csv(file)
    df.dropna(inplace=True)

    # Filter the dataframe based on the condition
    df = df[df['links'].str.contains('!Pinterest')]

    # Split the URL at the first occurrence of "!Pinterest"
    df['links'] = df['links'].str.split('!Pinterest', n=1, expand=True)[0]

    # Save the updated dataframe to a new CSV file
    # index = False to avoid saving the index column
    df.to_csv(file, index=False)

    print("Extracted all links successfully!")


###############################################################################

# Main Function
def main(url):
    # Extract the website name from the web link
    parsed_url = urlparse(url)
    website_name = parsed_url.netloc.replace('www.', '')
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Extract text after en/ from the URL
    fSlash = url.rsplit('/', 2)[-2]
    sSlash = url.rsplit('/', 1)[-1]
    filename = website_name + "_" + fSlash + "_" + sSlash + ".csv"

    page_content = get_content_from_url(url)
    image_urls = parse_image_urls(
        content=page_content, classes="ng-scope", location="img", source="src")

    save_urls_to_csv(image_urls, filename)
    extract_link_csv(filename)
    # download_image_to_file(filename)

###############################################################################


# Execute the main function
# Only executes if this file is run directly as a main entry file not as a imported one from some other python file.
if __name__ == "__main__":

    url = "https://www.wikiart.org/en/paintings-by-genre/cloudscape"
    # main(url)
    # download_image_to_file("wikiart.org.csv")

    df = pd.read_csv("1.URL.csv")
    for index, row in df.iterrows():
        url = row[0]
        # main(url)

    df = pd.read_csv("2.CSV File Names.csv")
    for index, row in df.iterrows():
        filename = row[0] + ".csv"
        download_image_to_file(filename)
