import re

from bs4 import BeautifulSoup
from bs4.element import Comment


WORD_LENGTH = 5
AVGERAGE_WPM = 200


def calc_reading_time(content_block):
    # Code based on:
    # https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
    # https://www.assafelovic.com/blog/2017/6/27/estimating-an-articles-reading-time
    soup = BeautifulSoup(content_block, 'html.parser')
    texts, content_length = soup.find_all(text=True), 0

    r = re.compile(r'\W', re.M | re.U)

    for text in texts:
        if isinstance(text, Comment):
            continue

        content_length += len(r.sub('', text))  # the number of alphanumeric characters in our text

    return (content_length / WORD_LENGTH) / AVGERAGE_WPM  # rough amount of time (minutes) required to read the content
