XKCD Crawler
by Jake Randolph Muncada

Python script that crawls through https://xkcd.com 
and downloads its comics along with the title and image tooltip comments.

The images will be downloaded to the 'output' directory which will be created
at the same location as this script.

The comic information (title and image comment) can be found in a JSON file
called 'xkcd.json' inside the output directory. This JSON file will be used
by subsequent executions of the script so that already downloaded pages
will be skipped.

Important:
If you wish to stop/terminate the script, press Ctrl+C instead of closing the
terminal/console window. This will allow the script to save its progress to 
the 'xkcd.json' file. (You may need to wait a few moments for the active threads
to finish their task.)


# INSTALLATION:
    You need to have python3 installed on your system.
    Next, install BeautifulSoup and requests libraries by executing the following command:
        pip3 install bs4 requests

# USAGE:
    Run main.py with command line arguments by executing the following command:
        python3 main.py [start] <end>

# EXAMPLES:
    python3 main.py 100 125     - Downloads chapters 100 to 125.
    python3 main.py 30          - Downloads chapter 1 to 30.

# NOTES:
    - Downloading is multi-threaded, meaning that multiple downloads can be active
      at any one time. The number of threads is set at 3 for now.

# FUTURE IMPROVEMENTS:
    - Allow the user to set the number of downloader threads.
    - Allow the user to set the output directory.
    - Allow the user to enable debug-level messages to be displayed on the console.
    - Allow the script to be run without arguments and automatically detect the last page of xkcd.
    - (Out Of Scope) Create an offline HTML page that can display the images along with its title
      and tooltip comment.
