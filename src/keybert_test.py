from base64 import urlsafe_b64decode

from keybert import KeyBERT

from src.gmail_func import gmail_authenticate, search_messages

doc = """
         Supervised learning is the machine learning task of learning a function that
         maps an input to an output based on example input-output pairs. It infers a
         function from labeled training data consisting of a set of training examples.
         In supervised learning, each example is a pair consisting of an input object
         (typically a vector) and a desired output value (also called the supervisory signal).
         A supervised learning algorithm analyzes the training data and produces an inferred function,
         which can be used for mapping new examples. An optimal scenario will allow for the
         algorithm to correctly determine the class labels for unseen instances. This requires
         the learning algorithm to generalize from the training data to unseen situations in a
         'reasonable' way (see inductive bias).
      """


def parse_parts(service, parts, message):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        if isinstance(parts, dict):
            parts = [parts]
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if part.get("parts"):
                # recursively call this function when we see that a part
                # has parts inside
                parse_parts(service, part.get("parts"), message)
            if mimeType == "text/plain":
                # if the email part is text plain
                if data:
                    text = urlsafe_b64decode(data).decode()
                    return text



def generate_text_from_msgs(service, gmail_msgs):
    """
    This function takes Gmail API `service` and the given `message_id` and does the following:
        - Downloads the content of the email
        - Prints email basic information (To, From, Subject & Date) and plain/text parts
        - Creates a folder for each email based on the subject
        - Downloads text/html content (if available) and saves it under the folder created as index.html
        - Downloads any file that is attached to the email and saves it in the folder created
    """
    for message in gmail_msgs:
        row = {"server_id": message['id']}
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        # parts can be the message body, or attachments
        payload = msg['payload']
        headers = payload.get("headers")
        parts = payload.get("parts")
        if parts is None:
            parts = payload
        return parse_parts(service, parts, message)



if __name__ == '__main__':

    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 3), top_n=1)
    print(keywords)

    # service = gmail_authenticate()
    #
    # # get emails that match the query you specify
    # results = search_messages(service, "RUTILEA")
    # text = generate_text_from_msgs(service, results)
    # print(text)
    # keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3))
    # print(keywords)



