from datetime import datetime

from sqlalchemy import insert, create_engine, select

from src.db_models import Mail, User, Base


def insert_into_tables(conn, mail_data):
    for mail_info in mail_data:
        mail_info['sender'] = get_user_id(conn, mail_info['sender'])
        mail_info['recipient'] = get_user_id(conn, mail_info['recipient'])
        print(mail_info)
    conn.execute(insert(Mail), mail_data)
    conn.commit()


def get_user_id(conn, user_info):
    name, addr = user_info.split('<')
    name = name.strip('\'" ')
    addr = addr.strip('\'" <>')
    id = conn.execute(select(User.id).where(
        User.email_address == addr,
        User.name == name)).scalar()
    if not id:  # not included in user db, need new insertion
        id = conn.execute(insert(User).values(email_address=addr, name=name).returning(
            User.id)).scalar()
        conn.commit()
    return id


def print_all_table(conn):
    stmt = select(User)
    for user in conn.execute(stmt):
        print(user)
    stmt = select(Mail)
    for mail in conn.execute(stmt):
        print(mail)


if __name__ == '__main__':
    data = [
        {'mail_server_id': '18bfd1199e673cc7', 'sender': '"LEGO® Shop" <Noreply@t.crm.lego.com>',
         'recipient': '<cyrilcao28@gmail.com>', 'keyword': '受付完了！ 行健様のご注文が確定しました。',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')},
        {'mail_server_id': '18bf1a0b42cfce45', 'sender': 'LinkedIn <messages-noreply@linkedin.com>',
         'keyword': ' Yilei, add Pankaj Gawande - Solution Architect - SAP BRIM at Acuiti Labs',
         'recipient': 'Yilei Cao <cyrilcao28@gmail.com>',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')}]
    engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        insert_into_tables(conn, data)
        print_all_table(conn)
