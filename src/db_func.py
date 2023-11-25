from datetime import datetime

from sqlalchemy import insert, create_engine, select

from src.db_models import Mail


def insert_into_table(conn, mail):


    result = conn.execute(insert(Mail), data)
    conn.commit()


def print_mails_table(conn):
    stmt = select(Mail)
    for mail in conn.execute(stmt):
        print(mail)


if __name__ == '__main__':
    data = [
        {'server_id': '18bfd1199e673cc7', 'sender': '"LEGO® Shop" <Noreply@t.crm.lego.com>',
         'recipient': '<cyrilcao28@gmail.com>', 'keyword': '受付完了！ 行健様のご注文が確定しました。',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')},
        {'server_id': '18bf1a0b42cfce45', 'sender': 'LinkedIn <messages-noreply@linkedin.com>',
         'keyword': ' Yilei, add Pankaj Gawande - Solution Architect - SAP BRIM at Acuiti Labs',
         'recipient': 'Yilei Cao <cyrilcao28@gmail.com>', 'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')}]
    engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
    with engine.connect() as conn:
        insert_into_table(conn, data)
        print_mails_table(conn)
