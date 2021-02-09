"""
An xkcd page.
"""

import os
import logging
from bs4 import BeautifulSoup
from downloader import Downloader


logger = logging.getLogger(__name__)


class Page:
    """
    A page of xkcd comic.

    Attributes:
        pageNum (int): The page number.
        pageUrl (str): The URL of the page.
        imageUrl (str): The URL of the image.
        title (str): The page title.
        comment (str): The image tooltip comment.
        path (str): The full path of the downloaded image.
        isDownloaded (bool): True if the image has been downloaded. False otherwise.
    """

    def __init__(self, pageNum, pageUrl, imageUrl, title, comment, path, isDownloaded):
        self.pageNum = pageNum
        self.pageUrl = pageUrl
        self.imageUrl = imageUrl
        self.title = title
        self.comment = comment
        self.path = path
        self.isDownloaded = isDownloaded

    def downloadImage(self, outputDir):
        """
        Download the image and save it to the given directory.

        Parameters:
            outputDir (str): The output directory.
        """
        if self.imageUrl is None:
            logger.error('Cannot download the image of page %d, image URL not found.', self.pageNum)
            return AttributeError('Image URL not found')

        filename = self.getImageFilename()
        outputPath = os.path.join(outputDir, filename)

        logger.debug('Downloading %s from %s...', filename, self.imageUrl)
        err = Downloader.downloadImage(self.imageUrl, outputPath)
        if err is not None:
            logger.error('Failed to download %s from %s, %s', filename, self.imageUrl, err)
            return err
        else:
            logger.debug('Successfully downloaded %s', filename)
            self.path = os.path.abspath(outputPath)
            self.isDownloaded = True
            return None

    def getImageFilename(self):
        """
        Returns the image filename.
        """
        # Get the filename from the image URL
        filename = self.imageUrl.rsplit('/', 1)[-1]
        # Check that the extension is an image
        validExts = ['.png', '.jpg', '.jpeg', '.gif']
        if not any([filename.endswith(ext) for ext in validExts]):
            logger.warning('"%s" is not a valid filename.', filename)
        # Add a 4-digit page number
        return f'{self.pageNum:04}_{filename}'

    def toDict(self):
        """
        Returns the dictionary representation.
        """
        result = {}
        result['pageNum'] = self.pageNum
        result['pageUrl'] = self.pageUrl
        result['imageUrl'] = self.imageUrl
        result['title'] = self.title
        result['comment'] = self.comment
        result['path'] = self.path
        result['isDownloaded'] = self.isDownloaded
        return result

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def fetch(cls, pageNum):
        """
        Instantiate a Page from its page number.
        The page HTML will be fetched and parsed.
        However, the image will not yet be downloaded.

        Parameters:
            pageNum (int): The page number.
        """
        soup = None
        url = Page.getPageUrl(pageNum)

        logger.debug('Fetching page %d...', pageNum)
        response, err = Downloader.get(url)
        if err is not None:
            logger.error('Failed to fetch %s, %s', url, Downloader.getErrorString(err))
            return None
        else:
            logger.debug('Successfully fetched page %s', pageNum)
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as err:  # pylint: disable=broad-except
                logger.error('Failed to parse %s to HTML soup, %s', url, err)
                return None

        return Page.fromSoup(pageNum, soup)

    @classmethod
    def fromSoup(cls, pageNum, soup):
        """
        Instantiate a Page from its soup.
        However, the image will not yet be downloaded.

        Parameters:
            pageNum (int): The page number.
            soup (BeautifulSoup): The page HTML soup.
        """
        pageUrl = Page.getPageUrl(pageNum)
        imageUrl = Page.getImageUrl(soup)
        title = Page.getPageTitle(soup)
        comment = Page.getImageComment(soup)
        # Return None if any of the above is None
        if any(x is None for x in [pageUrl, imageUrl, title, comment]):
            return None
        return cls(pageNum, pageUrl, imageUrl, title, comment, None, False)

    @classmethod
    def fromJson(cls, jsonData):
        """
        Instantiate a Page object from its JSON data.

        Parameters:
            jsonData (json): The JSON data.
        """
        pageNum = jsonData['pageNum']
        pageUrl = jsonData['pageUrl']
        imageUrl = jsonData['imageUrl']
        title = jsonData['title']
        comment = jsonData['comment']
        path = jsonData['path']
        isDownloaded = jsonData['isDownloaded']
        return cls(pageNum, pageUrl, imageUrl, title, comment, path, isDownloaded)

    ##################################################
    # STATIC METHODS
    ##################################################

    @staticmethod
    def getPageUrl(pageNum):
        """
        Get the page URL from the page number.

        Parameters:
            pageNum (int): The page number.

        Returns:
            str: The page URL.
        """
        return f'https://xkcd.com/{pageNum}'

    @staticmethod
    def getImageUrl(soup):
        """
        Parse the image URL from the soup.

        Parameters:
            soup (BeautifulSoup): The page's HTML soup.

        Returns:
            str: The image URL. Returns None if the parsing failed.
        """
        div = soup.find(id='comic') if soup is not None else None
        img = div.img if div is not None else None
        imageUrl = img.get('src') if img is not None else None
        if imageUrl is not None and imageUrl.startswith('//'):
            imageUrl = 'http:' + imageUrl
        return imageUrl

    @staticmethod
    def getPageTitle(soup):
        """
        Parse the page's title from the soup.

        Parameters:
            soup (BeautifulSoup): The page's HTML soup.

        Returns:
            str: The page title. Returns None if the parsing failed.
        """
        ctitle = soup.find(id='ctitle') if soup is not None else None
        pageTitle = ctitle.string if ctitle is not None else None
        return pageTitle

    @staticmethod
    def getImageComment(soup):
        """
        Parse the image tooltip comment from the soup.

        Parameters:
            soup (BeautifulSoup): The page's HTML soup.

        Returns:
            str: The image tooltip comment. Returns None if the parsing failed.
        """
        comic = soup.find(id='comic') if soup is not None else None
        img = comic.img if comic is not None else None
        comment = img.get('title') if img is not None else None
        return comment
