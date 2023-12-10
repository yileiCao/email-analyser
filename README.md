
# Email Analyser

This web application aids in managing a company’s email database effectively.

## Features

- Seamless integration with your Gmail account.
- Automatic keyword generation for each email added to the database.
- Semantic search functionality for finding related emails using keywords.
- Multi-user support, allowing simultaneous interaction with the app and facilitating email sharing.
- Easy integration with existing CRM systems.

## Preparing

- Clone this repository:
  
  git clone https://github.com/yileiCao/email-extraction.git

- Install the dependencies by simply executing:
  
  pip3 install -r requirements.txt
- Download nltk extensions in Python Console by:

  <code>import nltk</code>

  <code>nltk.download('wordnet')</code> to support semantic search

  <code>nltk.download('omw-1.4')</code> to support Japanese vocabulary set

- Get your Gmail credentials.json, and rename it with {{preferred_username}}_credentials.json.
  It should be uploaded after login.
  
  A test json is provided, test it by signing up a user with username=test.
  
  related link https://developers.google.com/gmail/api/quickstart/go 

- Run this command to start the app:
  
  <code>python run.py</code>

- Visit 127.0.0.1:8001 on your web browser to play around.

## Application preview
### Login page
![login_page](https://github.com/yileiCao/email-extraction/assets/63228731/ef99ffda-c98b-4f8f-8d28-b6bb0962ee64)

### Load mail page
![load_mails](https://github.com/yileiCao/email-extraction/assets/63228731/87412f74-a1b6-4a58-bbf6-03337336a197)

### Confirm mail insertion
![comfirm_email](https://github.com/yileiCao/email-extraction/assets/63228731/5c1cd7c9-8c27-4de6-bdb2-060d915d6fd3)

### Search mail page
![search_mails](https://github.com/yileiCao/email-extraction/assets/63228731/d9d023f1-e9f0-45f2-8054-ff6f74bf0ca0)

### Search mail results
![search_result](https://github.com/yileiCao/email-extraction/assets/63228731/b243bb4b-6ce8-409b-9cf5-6178cf24a183)

### View mail page
![mail_info1](https://github.com/yileiCao/email-extraction/assets/63228731/46991dc5-7453-4595-ad88-8f1a523df33e)

![keyword_update](https://github.com/yileiCao/email-extraction/assets/63228731/69cdf5ee-4ab3-42bc-8e92-08ed85e656d4)

![mail2](https://github.com/yileiCao/email-extraction/assets/63228731/23913dac-2c15-4f67-881f-d5f931369b6c)


###  Happy Exploring :)


