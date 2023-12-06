import os
import pickle
from dateutil import parser
from datetime import datetime, timezone

# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# If modifying these scopes, delete the file token.json.
from src.keybert_func import extract_keyword

SCOPES = ['https://mail.google.com/']
our_email = 'cyrilcao28@gmail.com'


def gmail_authenticate():
    ## TODO  personalized token
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("/Users/yileicao/Documents/email-extraction/src/token.pickle"):
        with open("/Users/yileicao/Documents/email-extraction/src/token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/yileicao/Documents/email-extraction/src/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("/Users/yileicao/Documents/email-extraction/src/token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def search_messages(service, query, get_all=True):
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    while get_all and 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages


def parse_body(body, content_type):
    """
    Utility function that parses the content of an email partition
    """
    text = ''
    if content_type == "text/plain":
        text = urlsafe_b64decode(body).decode()
    return text


def collect_head_info(headers, row):
    """
    :param headers: Gmail API returned header message
    :param row: generated info is stored in the row dictionary
    """
    for header in headers:
        name = header.get("name")
        value = header.get("value")
        if name.lower() == 'from':
            row["sender"] = value
        if name.lower() == "to":
            row["recipient"] = value
        if name.lower() == "subject":
            row["subject"] = value
        if name.lower() == "date":
            row["time"] = parser.parse(value).astimezone(timezone.utc)


def find_content(payload, content_type):
    if payload.get('mimeType') == content_type:
        return payload.get('body').get('data')
    elif payload.get('parts'):
        for part in payload.get('parts'):
            return find_content(part, content_type)


def generate_data_from_msgs(service, gmail_msgs):
    """
    :param service: Gmail API `service`
    :param gmail_msgs: Gmail list API returned messages
    :return: a list of dictionaries containing header information, plain text of the emails.
    """
    mails = []
    for idx, message in enumerate(gmail_msgs):
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        row = {"id": idx, "mail_server_id": msg['id'], "mail_thread_id": msg['threadId']}
        payload = msg['payload']
        headers = payload.get("headers")
        if headers:
            collect_head_info(headers, row)
        # print(row)

        # parts can be the message body, or attachments
        # if the msg contains only text part, 'parts' is empty while 'body' is not empty
        # if the msg contains multiple child MIME messages, 'body' is empty while 'parts' is not empty

        # only analyze text/plain
        text = find_content(payload, "text/plain")
        if text:
            text = parse_body(text, "text/plain")
            ##  TODO: Is there any better sulution?
            text = text.split('\n> ')[0]  # try removing duplicated earlier emails
        row['text'] = text
        mails.append(row)
    return mails


def data_extract_keyword(data):
    for mail in data:
        text = mail.pop('text')
        mail['keyword'] = ''
        if text:
            key_word = extract_keyword(text)
            mail['keyword'] = ', '.join([i[0] for i in key_word])


if __name__ == '__main__':
    # get the Gmail API service
    service = gmail_authenticate()
    # results = [{'id': '18bccbd2b9cc9308'}]

    # # get emails that match the query you specify
    results = search_messages(service, "RUTILEA") # only html: [{'id':'18be543e920c0596'}]
    # print(f"Found {len(results)} results.")
    # # for each email matched, read it (output plain/text to console & save HTML and attachments)
    generate_data_from_msgs(service, results)
