
# Email-extraction

A web application helps manage the email database for the company

## Features

- Easily connect with your Gmail account
- Automatically generate keywords for each mail loaded to the database
- Enable semantically search related emails by keywords
- Support multiple users to interact with the app at the same time, enable mail sharing
- Can be easily integrated into the CRM system

## Preparing

- Clone this repository:
  
  git clone https://github.com/yileiCao/email-extraction.git

- Install the dependencies by simply executing:
  
  pip3 install -r requirements.txt
- Download nltk extensions in Python Console by:

  <code>import nltk</code>

  <code>nltk.download('wordnet')</code> to support semantic search

  <code>nltk.download('omw-1.4')</code> to support Japanese vocabulary set

- Get your Gmail credentials.json, put it in src/credentials folder, and rename it with {{preferred_username}}_credentials.json
  
  A test json is provided, test it by signing up a user with username=test.
  
  related link https://developers.google.com/gmail/api/quickstart/go 

- Run this command to start the app:
  
  python run.py 

- Visit 127.0.0.1:8001 on your web browser to play around.

###  Happy Exploring :)


