import random
from selenium import webdriver
from time import sleep
import os
import logging

# my modules
from gmail import get_url_from_latest_email

# logger
formatter = logging.Formatter('%(asctime)s : %(module)s : %(funcName)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

__CHROMEDRIVER_FULL_PATH__ = os.environ.get('CHROMEDRIVER_FULL_PATH')


class WebBot:
    def __init__(self):
        logger.debug('Initializing a web bot.')
        self.driver = webdriver.Chrome(executable_path=__CHROMEDRIVER_FULL_PATH__)

    def click_button(self, url: str, x_path: str):
        logger.debug('Click a button from the following url: {}'.format(url))
        self.driver.get(url)
        seconds_to_sleep = random.randint(2, 6)
        logger.debug('Sleep for {} seconds.'.format(seconds_to_sleep))
        sleep(seconds_to_sleep)
        btn = self.driver.find_element_by_xpath(x_path)
        btn.click()


def main():
    from_email_address = "ENTER 'FROM' ADDRESS"
    email_subject = "ENTER SUBJECT"
    starting_url = "ENTER FIRST PARTS OF URL"  # e.g. https://www.
    x_path = ''

    # get the url
    url = get_url_from_latest_email(from_email_address, email_subject, starting_url)

    # initialize a web bot and click a button
    con_pas_bot = WebBot()
    con_pas_bot.click_button(url, x_path)


if __name__ == '__main__':
    main()

