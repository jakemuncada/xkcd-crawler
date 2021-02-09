"""
The main script.
"""

import os
import sys
import logging
from xkcd import XKCDCrawler


OUTPUT_DIR = './output'
JSON_FILEPATH = os.path.join(OUTPUT_DIR, 'xkcd.json')


def main():
    """
    The main function.
    """

    # Initialize logger
    initLogging()

    # Get the start and end pages from command line arguments
    start, end = getStartEnd()
    if start is None or end is None:
        printUsage()
        return

    # Create the output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Instantiate the xkcd crawler using the saved json if it exists
    if os.path.exists(JSON_FILEPATH):
        xkcd = XKCDCrawler.fromFile(JSON_FILEPATH)
    else:
        xkcd = XKCDCrawler()

    # Start downloading
    xkcd.download(start, end, './output')


def getStartEnd():
    """
    Get the start and end pages from the command line arguments.

    Returns:
        The start and end pages to be downloaded.
    """
    start = None
    end = None
    if len(sys.argv) == 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    elif len(sys.argv) == 2:
        start = 1
        end = int(sys.argv[1])
    return start, end


def printUsage():
    """
    Print the usage documentation.
    """

    lines = []
    lines.append('')
    lines.append('Provide either both start and end page numbers')
    lines.append('or just the end page number.')
    lines.append('')
    lines.append('Usage:')
    lines.append('   python3 main.py [start] <end>')
    lines.append('')
    lines.append('Example:')
    lines.append('   python3 main.py 100 125     - Downloads pages 100 to 125.')
    lines.append('   python3 main.py 30          - Downloads pages 1 to 30.')
    lines.append('')
    print('\n'.join(lines))


def initLogging():
    """
    Initialize the logger.
    """

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)

    handler = logging.StreamHandler()

    # Set formatter to print only the message in console
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    # Set level to INFO
    handler.setLevel(logging.INFO)

    logging.getLogger().addHandler(handler)


if __name__ == '__main__':
    main()
