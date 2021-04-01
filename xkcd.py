"""
Web crawler for xkcd.com for downloading its comics.
"""

import os
import json
import logging
from time import sleep
from queue import Queue
from threading import Thread, Event
from tqdm import tqdm
from page import Page


logger = logging.getLogger(__name__)


class XKCDCrawler:
    """
    Web crawler for xkcd.com for downloading its comics.
    """

    def __init__(self, pages=None):
        self.pages = pages if pages is not None else {}

    @classmethod
    def fromFile(cls, filepath):
        """
        Initialize the XKCDCrawler from its json cache file.

        Parameters:
            filepath (str): The path of the json cache file.

        Returns:
            The initialized XKCDCrawler.
        """
        with open(filepath, 'r') as inputFile:
            jsonData = json.load(inputFile)
            return XKCDCrawler.fromJson(jsonData)

    @classmethod
    def fromJson(cls, jsonData):
        """
        Initialize the XKCDCrawler from its json cache object.

        Parameters:
            jsonData (str): The path of the json cache object.

        Returns:
            The initialized XKCDCrawler.
        """
        pages = {}
        for pageNumStr in jsonData:
            page = Page.fromJson(jsonData[pageNumStr])
            pages[pageNumStr] = page
        return cls(pages)

    def download(self, start, end, outputDir, threads=3):
        """
        Start the download.

        Parameters:
            start (int): The start page number.
            end (int): The end page number.
            outputDir (str): The output directory.
            threads (int): The number of threads.
        """
        killEvent = Event()
        failedPages = Queue()

        queue = Queue()
        for pageNum in range(start, end + 1):
            queue.put(pageNum)

        total = (end - start) + 1
        pbar = tqdm(total=total, unit="pages", desc="Downloading xkcd pages")

        _threads = []
        for _ in range(threads):
            t = Thread(target=self.process, args=(queue, pbar, outputDir, killEvent, failedPages))
            _threads.append(t)
            t.start()

        try:
            while not queue.empty():
                sleep(0.3)

            for t in _threads:
                t.join()

        except KeyboardInterrupt:
            killEvent.set()
            pbar.close()
            logger.info('Stopping threads... Please wait for active threads to finish...')
            for t in _threads:
                t.join()

        finally:
            # Close the progress bar
            pbar.close()
            # Print the list of pages that weren't downloaded
            if not failedPages.empty():
                logger.info('Failed to download the following pages:')
                while not failedPages.empty():
                    logger.info('   %s', failedPages.get())
            # Save xkcd.json file
            self.save(outputDir)

    def process(self, queue, pbar, outputDir, killEvent, failedPages):
        """
        The process function of each thread.

        Parameters:
            queue (queue of int): The download queue.
            pbar (tqdm): The progress bar.
            outputDir (str): The output directory.
            killEvent (threading.Event): The event object that can terminate the process.
            failedPages (queue of Pages): The collection of Pages that failed to be downloaded.
        """
        while not queue.empty() and not killEvent.is_set():
            pageNum = queue.get()
            pageNumStr = f'{pageNum:04}'

            if pageNum == 404:
                # Skip the 404 error page, haha
                logger.debug('Skipping the intentional 404 Error page...')
            elif pageNumStr in self.pages and self.pages[pageNumStr].isDownloaded:
                logger.debug('Skipping page %d...', pageNum)
            else:
                page = Page.fetch(pageNum)
                self.pages[pageNumStr] = page
                err = page.downloadImage(outputDir)
                if err is not None:
                    failedPages.put(Page.getPageUrl(pageNum))

            pbar.update()
            queue.task_done()

    def save(self, outputDir):
        """
        Save the cache to a json file.

        Parameters:
            outputDir (str): The output directory.
        """
        filename = 'xkcd.json'
        filepath = os.path.join(outputDir, filename)

        logger.info('Saving %s to %s...', filename, outputDir)
        with open(filepath, 'w') as writer:
            jsonStr = json.dumps(self.toDict(), indent=4, sort_keys=True)
            writer.write(jsonStr)
            logger.info('%s saved successfully.', filename)

    def toDict(self):
        """
        Convert the crawler data to a dictionary.

        Returns:
            The dictionary representation of the crawler data.
        """
        result = {}
        for pageNum in self.pages:
            result[pageNum] = self.pages[pageNum].toDict()
        return result
