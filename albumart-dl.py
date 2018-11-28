#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download HQ album cover art
"""

__version__ = "0.1.0"

import argparse
import os
import logging
import logging.handlers
import socket
import string
import unicodedata

from multiprocessing import Pool
from sys import exit
from time import time

# External dependencies
from halo import Halo
from requests import get

LOGGER = logging.getLogger(__name__)
OPTION_GROUP = argparse.Namespace()


def setup_logging():
    """Sets up logging in a syslog format by log level
    :param OPTION_GROUP: options as returned by the OptionParser
    """
    stderr_log_format = "%(levelname)s %(message)s"
    file_log_format = "%(asctime)s - %(levelname)s - %(message)s"
    LOGGER.setLevel(level=OPTION_GROUP.loglevel)

    handlers = []
    if OPTION_GROUP.logfile:
        handlers.append(logging.FileHandler(OPTION_GROUP.logfile))
        handlers[0].setFormatter(logging.Formatter(file_log_format))
    if not handlers:
        handlers.append(logging.StreamHandler())
        handlers[0].setFormatter(logging.Formatter(stderr_log_format))
    # Remove all the old handler(s)
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    # Add our new handler(s) back in
    for handler in handlers:
        logging.root.addHandler(handler)

    LOGGER.debug("Exiting 'setup_logging()'")
    return


# Create network connection
def connect(host, port):
    LOGGER.debug("Entered 'connect()'")

    try:
        # Connect to the host
        with socket.create_connection((host, port), timeout=5):
            return True
    except (socket.error, socket.gaierror):
        LOGGER.error(f"🚩 Could not connect to '{host}'. Are you online?")
        exit(1)


# Sanitize strings to create valid file names
def clean_filename(filename, replace=" "):
    LOGGER.debug("Entered 'clean_filename()'")

    valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    char_limit = 255

    # Replace spaces
    for r in replace:
        filename = filename.replace(r, "_")

    # Keep only valid ASCII chars
    cleaned_filename = (
        unicodedata.normalize("NFKD", filename).encode("ASCII", "ignore").decode()
    )

    # Keep only whitelisted chars
    cleaned_filename = "".join(c for c in cleaned_filename if c in valid_filename_chars)
    if len(cleaned_filename) > char_limit:
        LOGGER.warning(
            "🚩 Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(
                char_limit
            )
        )
    return cleaned_filename[:char_limit]


# Timer to measure total execution time
def timer(func):
    LOGGER.debug("Entered 'timer()'")

    def f(*args, **kwargs):
        before = time()
        rv = func(*args, **kwargs)
        after = time()
        print("⏱️  Time to download:", round(after - before, 2), "seconds")
        return rv

    return f


# Download and save album art to disk
def search_album_art(query, output_path):
    LOGGER.debug("Entered 'search_album_art()'")

    # List to hold our image URLs
    image_urls = []

    # Replace blank spaces from search query
    queryString = query.replace(" ", "%20")

    # Download album art data from iTunes API
    res = get(url=f"https://itunes.apple.com/search?term={queryString}&entity=album")

    # Check that request succeeded, will raise an exception if HTTP status code is not 200
    try:
        res.raise_for_status()
    except:
        LOGGER.error("🚩 Error while trying to access API")
        exit(1)

    data = res.json()

    # Check if results are empty
    if data["resultCount"] == 0:
        LOGGER.error(f"🚩 Sorry. Could not find any album art for '{query}'.")
        exit(1)

    # Create user provided output_path if it doesn't exist
    if output_path and not os.path.isdir(output_path):
        os.makedirs(output_path)
    # If no output_path has been provided create one
    elif not output_path:
        output_path = os.path.join(os.getcwd(), str(query) + " - Album Art")
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

    # Iterate over albums and populate our image_urls list with tuples of (output_path, image_url)
    for album in data["results"]:
        imagePath = os.path.join(
            output_path, clean_filename(album["collectionName"]) + ".jpg"
        )
        # Download high quality version of art work by replacing JPG sizes in URL
        imageUrl = album["artworkUrl100"].replace("100x100bb.jpg", "5000x5000bb.jpg")
        image_urls.append((imagePath, imageUrl))

    return image_urls


# Download binary file from URL
def download_image(url):
    LOGGER.debug("Entered 'download_image()'")
    path, uri = url
    if not os.path.isfile(path):
        r = get(uri, stream=True)
        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r:
                    f.write(chunk)
    LOGGER.info(f"Downloading: {path}")


@timer
def main():
    """Primary entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # Standard logging options.
    parser.add_argument(
        "search",
        action="store",
        metavar="Artist name",
        help="Artist name to download album art for",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.INFO,
        dest="loglevel",
        default=logging.WARNING,
        help="Verbose output",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="loglevel",
        default=logging.WARNING,
        help="Debugging output",
    )
    parser.add_argument(
        "--logfile", metavar="", help="Path to file to store log messages"
    )
    parser.add_argument(
        "-o",
        "--output-path",
        action="store",
        metavar="",
        help="Path to folder where to store album art files",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
        help="Display app version",
    )

    # Script-specific options here
    parser.parse_args(namespace=OPTION_GROUP)
    setup_logging()

    # Check for link URL
    if OPTION_GROUP.output_path:
        LOGGER.debug("'--output_path' flag has been specified.")

    host = "itunes.apple.com"
    connect(host, 443)

    try:
        urls = search_album_art(OPTION_GROUP.search, OPTION_GROUP.output_path)

        # Start waiting animation
        with Halo(text="Downloading files …", spinner="dots"):
            # Download album art images in parallel
            with Pool(10) as p:
                p.map(download_image, urls)
    except Exception as e:
        LOGGER.critical("🚩 There was an error:", e)
    else:
        print("👍 Album art downloaded successfully.")


if __name__ == "__main__":
    main()
