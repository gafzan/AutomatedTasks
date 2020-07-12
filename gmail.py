import imaplib
import email
from email import policy
from bs4 import BeautifulSoup

import os
import logging

__USERNAME__ = os.environ.get('GMAIL_USERNAME')
__PASSWORD__ = os.environ.get('GMAIL_PASSWORD')
__SERVER_MAIL__ = 'imap.gmail.com'  # server mail used to read incoming mail


# logger
formatter = logging.Formatter('%(asctime)s : %(module)s : %(funcName)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def email_connection():
    # initialize a connection
    con = imaplib.IMAP4_SSL(__SERVER_MAIL__)
    con.login(__USERNAME__, __PASSWORD__)  # authenticate
    return con


def get_url_from_latest_email(from_: str, subject_: str, url_first_part: str):
    logger.debug('Retrieve the URL from the latest email from {} with the subject {}.'.format(from_, subject_))
    # setup your email connection
    mail_con = email_connection()
    mail_con.select('Inbox')

    # search based on the email adress (from) and save a list with all the byte data
    data = mail_con.uid('search', None, 'FROM "{}"'.format(from_))[1]  # returns ('OK', list of bytes)
    inbox_item_list = data[0].split()  # data is a list with a one byte string (so let's make it into a real list)

    # fetch data for the latest email item (inbox_item_list has the oldest email item as its first element)
    email_data = mail_con.uid('fetch', inbox_item_list[-1], '(RFC822)')[1]

    # email data is a list of tuples containing bytes [(bytes, ...
    # pick the first tuple in the list and the second byte from that tuple and decode it
    raw_email = email_data[0][1].decode('utf-8')

    # initialize an email object
    email_msg = email.message_from_string(raw_email, policy=policy.default)  # alt. email.message_from_bytes(email_data[0][1])
    # check the subject of the latest email
    if subject_ != email_msg['Subject']:
        raise ValueError('Subject in the latest email from {} does not equal {}.'.format(from_, subject_))

    for part in email_msg.walk():  # we will "walk" through the parts of the email message
        if part.get_content_maintype() == 'multipart':
            continue
        content_type = part.get_content_type()
        if 'plain' in content_type:
            plain_text_split = part.get_content().split()
        elif 'html' in content_type:
            # use beautiful soup to extract the text from the HTLM file
            html_ = part.get_content()
            soup = BeautifulSoup(html_, 'html.parser')
            text = soup.get_text()
            plain_text_split = text.split()
        else:
            continue
        for plain_txt in plain_text_split:
            if plain_txt.startswith(url_first_part):
                return plain_txt


def mail_lab(from_: str, subject: str):
    con = email_connection()
    con.select('Inbox')

    search_criteria = '(FROM "{}" SUBJECT "{}")'.format(from_, subject)
    result, data = con.uid('search', None, search_criteria)  # gets the unique identification for the actual items
    inbox_item_list = data[0].split()  # data is a list with a one byte string (so let's make it into a real list)

    for item in inbox_item_list:  # loop through each byte string
        result2, email_data = con.uid('fetch', item, '(RFC822)')  # fetch data for a specific email
        # email data is a list of tuples containing bytes [(bytes, ...
        # pick the first tuple in the list and the second byte from that tuple and decode it
        raw_email = email_data[0][1].decode('utf-8')

        # convert into an email object
        email_msg = email.message_from_string(raw_email)  # alt. email.message_from_bytes(email_data[0][1])
        to = email_msg['To']
        from_ = email_msg['From']
        subject = email_msg['Subject']

        # emails can be in one or several parts
        counter = 1
        for part in email_msg.walk():  # we will "walk" through the parts of the message
            print('#{} email'.format(counter))
            # save file
            content_type = part.get_content_type()
            print(content_type)
            print(subject)
            if 'plain' in content_type:
                print(part.get_payload().encode("utf-8"))
            elif 'html' in content_type:
                print('Dos some beautiful soup')
            else:
                print(content_type)
            counter += 1

