from datetime import datetime

from sqlalchemy import insert, create_engine, select
from sqlalchemy.orm import Session

from src.db_models import Mail, User, Base


def insert_into_tables(session, mail_data):
    for mail_info in mail_data:
        mail_info['sender'] = get_user_id(session, mail_info['sender'])
        mail_info['recipient'] = get_user_id(session, mail_info['recipient'])
        # print(mail_info)
    if mail_data:
        # session.execute(insert(Mail), mail_data)
        for mail in mail_data:
            if session.execute(select(Mail.id).where(
                    Mail.mail_server_id == mail['mail_server_id'])).all():
                continue
            session.merge(Mail(**mail))
        session.commit()


def get_user_id(session, user_info):
    try:
        name, addr = user_info.split('<')
    except ValueError:
        name, addr = None, user_info
    if isinstance(name, str):
        name = name.strip('\'" ')
    addr = addr.strip('\'" <>')
    id = session.execute(select(User.id).where(
        User.email_address == addr,
        User.name == name)).scalar()
    if not id:  # not included in user db, need new insertion
        id = session.execute(insert(User).values(email_address=addr, name=name).returning(
            User.id)).scalar()
        session.commit()
    return id


def print_all_table(session):
    stmt = select(User)
    for user in session.execute(stmt):
        print(user)
    stmt = select(Mail)
    for mail in session.execute(stmt):
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
    with Session(engine) as session:
        insert_into_tables(session, data)
        print_all_table(session)
