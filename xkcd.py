"""
Web crawler for xkcd.com for downloading its comics.
"""

import os
import json
import logging
from time import sleep

from page import Page
from queue import Queue
from threading import Thread, Event


logger = logging.getLogger(__name__)


class XKCDCrawler:
    """
    Web crawler for xkcd.com for downloading its comics.
    """

    def __init__(self, pages=None):
        self.pages = pages if pages is not None else {}

    @classmethod
    def fromFile(cls, filepath):
        with open(filepath, 'r') as inputFile:
            jsonData = json.load(inputFile)
            return XKCDCrawler.fromJson(jsonData)

    @classmethod
    def fromJson(cls, jsonData):
        pages = {}
        for pageNumStr in jsonData:
            page = Page.fromJson(jsonData[pageNumStr])
            pages[pageNumStr] = page
        return cls(pages)

    def download(self, start, end, outputDir, threads=3):
        killEvent = Event()
        failedPages = Queue()

        queue = Queue()
        for pageNum in range(start, end + 1):
            queue.put(pageNum)

        _threads = []
        for _ in range(threads):
            t = Thread(target=self.process, args=(queue, outputDir, killEvent, failedPages))
            _threads.append(t)
            t.start()

        try:
            while not queue.empty():
                sleep(0.3)

            for t in _threads:
                t.join()

            logger.info('Finished processing pages %d to %d.', start, end)

        except KeyboardInterrupt:
            killEvent.set()
            logger.info('Stopping threads... Please wait for active threads to finish...')
            for t in _threads:
                t.join()

        finally:
            # Print the list of pages that weren't downloaded
            if not failedPages.empty():
                logger.info('Failed to download the following pages:')
                while not failedPages.empty():
                    logger.info('   %s', failedPages.get())
            # Save xkcd.json file
            self.save(outputDir)

    def process(self, queue, outputDir, killEvent, failedPages):
        while not queue.empty() and not killEvent.is_set():
            pageNum = queue.get()
            pageNumStr = f'{pageNum:04}'

            if pageNum == 404:
                # Skip the 404 error page, haha
                logger.info('Skipping the intentional 404 Error page...')
            elif pageNumStr in self.pages and self.pages[pageNumStr].isDownloaded:
                logger.info('Skipping page %d...', pageNum)
            else:
                logger.info('Processing page %d...', pageNum)
                page = Page.fetch(pageNum)
                self.pages[pageNumStr] = page
                err = page.downloadImage(outputDir)
                if err is not None:
                    failedPages.put(Page.getPageUrl(pageNum))

            queue.task_done()

    def save(self, outputDir):
        filename = 'xkcd.json'
        filepath = os.path.join(outputDir, filename)

        logger.info('Saving %s to %s...', filename, outputDir)
        with open(filepath, 'w') as writer:
            jsonStr = json.dumps(self.toDict(), indent=4, sort_keys=True)
            writer.write(jsonStr)
            logger.info('%s saved successfully.', filename)

    def toDict(self):
        result = {}
        for pageNum in self.pages:
            result[pageNum] = self.pages[pageNum].toDict()
        return result
