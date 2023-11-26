from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db_func import insert_into_tables, print_all_table
from src.db_models import Base
from src.gmail_func import gmail_authenticate, search_messages, generate_data_from_msgs

if __name__ == '__main__':
    engine = create_engine("sqlite://", echo=False)
    # engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
    Base.metadata.create_all(engine)

    service = gmail_authenticate()

    # get emails that match the query you specify
    results = search_messages(service, "RETILEA")
    print(f"Found {len(results)} results.")
    # for each email matched, read it (output plain/text to console & save HTML and attachments)
    data = generate_data_from_msgs(service, results)
    print(data)
    with engine.connect() as conn:
        insert_into_tables(conn, data)
        print_all_table(conn)
