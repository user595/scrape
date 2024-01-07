""" download a webpage and contents """
import os
import argparse

from urllib.parse import urljoin, urlparse
import logging

from bs4 import BeautifulSoup
import requests

def setup_logging(plog_level):
    """Set up logging configuration based on the provided log level."""
    logging.debug(f"setup_logging({plog_level})")
    # Set up logging to console and file
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Create a folder for log files
    log_folder = 'logs'
    os.makedirs(log_folder, exist_ok=True)

    # Specify the log file path
    log_file_path = os.path.join(log_folder, 'app.log')

    logging.basicConfig(
        level=plog_level,  # Set the logging level
        format="%(asctime)s - %(levelname)s - %(message)s",  # Specify log message format
        handlers=[
            logging.StreamHandler(),  # Log to the console
        ]
    )

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)

def getURLData(url):
    try:
        response = ""
        # Make a request to the main page to extract links
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
            #errors related to making requests, including network errors
            print(f"Request failed: {e}")
            logging.info(f"scan_page:requests.get({url}) exception {e}")
    except requests.exceptions.HTTPError as e:
            #errors returned by the server (e.g., 404 Not Found, 500 Internal Server Error)
            print(f"HTTP error occurred: {e}")
            logging.info(f"scan_page:requests.get({url}) exception {e}")
    except requests.exceptions.ConnectionError as e:
            #connection-related errors, such as DNS resolution failure, network unreachable, 
            #or connection refused
            print(f"Connection error occurred: {e}")
            logging.info(f"scan_page:requests.get({url}) exception {e}")
    except requests.exceptions.Timeout as e:
            #request times out, i.e., the server does not respond within the specified timeout period
            print(f"Request timed out: {e}")
            logging.info(f"scan_page:requests.get({url}) exception {e}")
    except requests.exceptions.MissingSchema as e:
            #URL provided to requests.get is not well-formed (missing the scheme, 
            #e.g., "example.com" instead of "http://example.com").
            print(f"Invalid URL: {e}")
            logging.info(f"scan_page:requests.get({url}) exception {e}")
    return response

def get_data(pweb_address,output_folder,tags):
    count = len(tags)
    item = 1
    for tag in tags:
        print(f"Processing {pweb_address} item {item} of {count}")
        # Construct absolute URL using urljoin
        if ('src' in tag.attrs):
            url = urljoin(pweb_address, tag['src'])
        if ('href' in tag.attrs):
            url = urljoin(pweb_address, tag['href'])
        # Log the image URL before downloading
        logging.info(f"Downloading data: {url}")

        # Download each image
        download_file(url, output_folder)
        item = item + 1
    return #for debugging purposes

def download_file(file_url, base_path):
    """ download a file"""
    # Parse the file URL to extract the filename
    logging.debug(f"download_file({file_url}, {base_path})")
    file_filename = os.path.basename(urlparse(file_url).path)

    file_response = getURLData(file_url)

    if file_response != '': 
        if file_response.status_code == 200: 
        #added to check if valid file i.e. mailto address

            file_path = os.path.join(base_path, file_filename)

            # Check if the file is not a directory before opening it
            if not os.path.isdir(file_path):
                with open(file_path, 'wb') as file_file:
                    file_file.write(file_response.content)

                logging.info(f"File downloaded: {file_url}")
            else:
                logging.warning(f"Skipping directory: {file_url}")
    return #for debugging purposes

def scrape_website(pweb_address):
    """ Create a folder to store the downloaded webpages"""
    logging.debug(f"scrape_website({pweb_address})")
    #pdb.set_trace()
    output_folder = 'downloaded_pages'
    os.makedirs(output_folder, exist_ok=True)

    response = getURLData(pweb_address)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all links on the page
        links = soup.find_all('a', href=True)
        #convert to set then back to list to remove duplicates
        result_set = set(links)
        links = list(result_set) 
        get_data(pweb_address,output_folder,links)

        #download the items on the main page
        # Find all image tags in the HTML
        img_tags = soup.find_all('img', src=True)
        #convert to set then back to list to remove duplicates
        result_set = set(img_tags)
        img_tags = list(result_set) 
        get_data(pweb_address,output_folder,img_tags)
    else:
        print(f"Failed to fetch main page: {pweb_address}")

if __name__ == "__main__":
    logging.debug("__main__")
    # Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description="dynamic logging level")

    parser.add_argument(
        "--path",
        help="the http path i.e. https://www.pollardbanknote.com/company/",
        default="https://www.pollardbanknote.com/company/"
        #default="https://www.lottery.ok.gov/scratchers/492108"
        #default="https://www.gutenberg.org/ebooks/2701"
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],  # Allow only valid log levels
        default="INFO",  # Default logging level if not provided
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Convert the log level argument to the corresponding logging constant
    loglevel = getattr(logging, args.loglevel)

    # Set up logging configuration based on the provided log level
    print(f"log set to {loglevel}")
    setup_logging(loglevel)

    web_address = args.path
    scrape_website(web_address)