from datetime import datetime

from sqlalchemy import create_engine, insert

from src.db_func import get_user_id, insert_into_tables, print_all_table
from src.db_models import Base, User


def generate_user_data(conn):
    data = [{'name': 'aa', 'email_address': 'aa@email.com'},
            {'name': 'bb', 'email_address': 'bb@bmail.com'}]
    conn.execute(insert(User), data)
    conn.commit()


def generate_mail_data(conn):
    data = [
        {'server_id': '18bfd1199e673cc7', 'sender': '"LEGO® Shop" <Noreply@t.crm.lego.com>',
         'recipient': '<cyrilcao28@gmail.com>', 'keyword': '受付完了！ 行健様のご注文が確定しました。',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')},
        {'server_id': '18bf1a0b42cfce45', 'sender': 'LinkedIn <messages-noreply@linkedin.com>',
         'keyword': ' Yilei, add Pankaj Gawande - Solution Architect - SAP BRIM at Acuiti Labs',
         'recipient': 'Yilei Cao <cyrilcao28@gmail.com>',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')}]
    insert_into_tables(conn, data)
    print_all_table(conn)


def test_get_user_id(conn):
    user_info1 = '"aa "<aa@email.com>'
    user_info2 = '"bb "<aa@email.com>'
    result1 = get_user_id(conn, user_info1)
    assert(result1 == 1)
    result2 = get_user_id(conn, user_info2)
    assert(result2 == 3)


if __name__ == '__main__':

    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        generate_user_data(conn)
        test_get_user_id(conn)