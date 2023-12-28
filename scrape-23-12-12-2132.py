#import pdb; #pdb.set_trace()
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import argparse
import sys

def setup_logging(log_level):
    """Set up logging configuration based on the provided log level."""
    logging.debug(f"setup_logging({log_level})")
    #pdb.set_trace()
    # Set up logging to console and file
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    #logging.basicConfig(level=logging.DEBUG, format=log_format)
    
    # Create a folder for log files
    log_folder = 'logs'
    os.makedirs(log_folder, exist_ok=True)
    
    # Specify the log file path
    log_file_path = os.path.join(log_folder, 'app.log')

    logging.basicConfig(
        level=log_level,  # Set the logging level
        format="%(asctime)s - %(levelname)s - %(message)s",  # Specify log message format
        handlers=[
            logging.StreamHandler(),  # Log to the console
            # Add more handlers if needed (e.g., logging.FileHandler for logging to a file)
            # Add a file handler to write logs to the file
        ]
    )
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)

def is_html_path(url):
    """ return True of False - is this a htm or html path from the url """
    parsed_url = urlparse(url)
    path = parsed_url.path

    # Check if the path ends with ".html" or ".htm"
    return path.lower().endswith((".html", ".htm"))

def download_page(url, base_path):#rename to scan_page?
    # Parse the URL to extract the path
    #logging.debug(f"download_page({url}, {base_path})")
    print(f"download_page({url}, {base_path})")
    #pdb.set_trace()
    parsed_url = urlparse(url)
    
    # Log a debug message
    logging.debug(f"Downloading page: {url}")

    #is this causing files to NOT download non-jpg png info?
    # Check if the path is a directory
    #if not parsed_url.path or parsed_url.path.endswith('/'):
    #    #could recursive call function download_page with this url 
    #    logging.info(f"Skipping directory: {url}")
    #    return

    #is this causing files to NOT download non-jpg png info?
    logging.info(f"is_html_path: {url}")
    # Check if this is a htm or html file
    if (is_html_path(url)==False):
        logging.info(f"is_html_path: {url} False - not a htm or html file")
        return;

    # Continue with downloading the page
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all image tags in the HTML
        img_tags = soup.find_all('img', src=True)
        for img_tag in img_tags:
            # Construct absolute image URL using urljoin
            img_url = urljoin(url, img_tag['src'])
            
            # Log the image URL before downloading
            logging.info(f"Downloading image: {img_url}")
            
            # Download each image
            download_file(img_url, base_path)
        
        # Find all PDF links in the HTML
        pdf_tags = soup.find_all('a', href=True)
        for pdf_tag in pdf_tags:
            pdf_url = urljoin(url, pdf_tag['href'])
            
            # Log the PDF URL before downloading
            logging.info(f"Downloading PDF: {pdf_url}")
            
            # Download each PDF
            download_file(pdf_url, base_path)
    else:
        logging.debug(f"Failed to fetch page: {url}")

def download_file(file_url, base_path):
    # Parse the file URL to extract the filename
    logging.debug(f"download_file({file_url}, {base_path})")
    file_filename = os.path.basename(urlparse(file_url).path)

    try:
        # Download the file and save it to the base path
        file_response = requests.get(file_url)
        file_response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        file_path = os.path.join(base_path, file_filename)

        # Check if the file is not a directory before opening it
        if not os.path.isdir(file_path):
            with open(file_path, 'wb') as file_file:
                file_file.write(file_response.content)
            
            logging.info(f"File downloaded: {file_url}")
        else:
            logging.warning(f"Skipping directory: {file_url}")
    except requests.exceptions.RequestException as e:
        # Log an error if there's an issue downloading the file
        logging.debug(f"Failed to download file: {file_url} - {e}")

def scrape_website(web_address):
    # Create a folder to store the downloaded webpages
    logging.debug(f"scrape_website({web_address})")
    #pdb.set_trace()
    output_folder = 'downloaded_pages'
    os.makedirs(output_folder, exist_ok=True)

    # Make a request to the main page to extract links
    response = requests.get(web_address)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links on the page
        links = soup.find_all('a', href=True)
        for link in links:
            link_url = link['href']

            # Construct absolute URL using urljoin
            absolute_url = urljoin(web_address, link_url)

            # Log the URL before downloading
            logging.info(f"Downloading page: {absolute_url}")
            
            # Download each linked webpage
            download_page(absolute_url, output_folder)
    
            # Find all image tags in the HTML
            img_tags = soup.find_all('img', src=True)
            for img_tag in img_tags:
                # Construct absolute image URL using urljoin
                img_url = urljoin(web_address, img_tag['src'])
                
                # Log the image URL before downloading
                logging.info(f"Downloading image: {img_url}")
                
                # Download each image
                download_file(img_url, output_folder)    
    
    else:
        print(f"Failed to fetch main page: {web_address}")
        
if __name__ == "__main__":
    logging.debug("__main__")
    #import sys
    #pdb.set_trace()
    # Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description="dynamic logging level")

    # Add an argument for specifying the logging level
    parser.add_argument(
        "path",help="the http path"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],  # Allow only valid log levels
        default="INFO",  # Default logging level if not provided
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    #pdb.set_trace()

    # Parse command-line arguments
    args = parser.parse_args()
    
    # Convert the log level argument to the corresponding logging constant
    log_level = getattr(logging, args.log_level)

    # Set up logging configuration based on the provided log level
    #pdb.set_trace()
    setup_logging(log_level)

    #pdb.set_trace()
    
    # Check if a web address is provided as a command line argument
    #if len(sys.argv) < 2:#how many arguments are there?
    #    print("Usage: python script.py <web_address>")
    #    sys.exit(1)

    #web_address = sys.argv[1]#web address might be any argument 0 - ...
    web_address = args.path
    #pdb.set_trace()
    scrape_website(web_address)