
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
![confirm](https://github.com/yileiCao/email-analyser/assets/63228731/cb569f28-e1ca-4bee-beef-6da30c080711)

### Search mail page
![search_email](https://github.com/yileiCao/email-analyser/assets/63228731/bc040db4-9978-41ce-ba36-7c0ed9652a65)

### Search mail results
![search_result](https://github.com/yileiCao/email-analyser/assets/63228731/6d301b05-7fba-48e6-8190-5f9dd4985f88)

### View mail page
![email_info1](https://github.com/yileiCao/email-analyser/assets/63228731/473a10b2-cad0-4500-ae98-379fabb4a7fc)

![keyword_update](https://github.com/yileiCao/email-analyser/assets/63228731/94c72a84-334f-4422-8491-8efd70fa21ff)

![mail2](https://github.com/yileiCao/email-extraction/assets/63228731/23913dac-2c15-4f67-881f-d5f931369b6c)


###  Happy Exploring :)


