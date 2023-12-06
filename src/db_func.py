from datetime import datetime

from sqlalchemy import insert, create_engine, select, text, func
from sqlalchemy.orm import Session, aliased

from src.db_models import Mail, User, Base
from src.wordnet_func import get_lemmas_en, get_lemmas_jpn


def insert_into_tables(session, mail_data):
    num_succeed = len(mail_data)
    for mail_info in mail_data:
        mail_info['sender'] = get_user_id(session, mail_info['sender'])
        mail_info['recipient'] = get_user_id(session, mail_info['recipient'])
        # print(mail_info)
    if mail_data:
        # session.execute(insert(Mail), mail_data)
        for mail in mail_data:
            if session.execute(select(Mail.id).where(
                    Mail.mail_server_id == mail['mail_server_id'])).all():
                num_succeed -= 1
                continue
            session.merge(Mail(**mail))
        session.commit()
    return num_succeed


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


def build_select_statement(filters):
    userR = aliased(User, name="userR")
    userS = aliased(User, name="userS")
    query = \
        select(userS.name, userS.email_address, userR.name, userR.email_address,
               Mail.mail_server_id, Mail.subject, Mail.keyword, Mail.time, Mail.id) \
            .join(userS, Mail.sender_user).join(userR, Mail.recipient_user) \
            .order_by(Mail.time.desc())
    if filters.get("fr"):  # sender email_address
        query = query.where(userS.email_address == filters["fr"])
    if filters.get("to"):  # recipient email_address
        query = query.where(userR.email_address == filters["to"])
    if filters.get('be'):  # time before
        query = query.where(func.date(Mail.time) <= filters['be'])
    if filters.get('af'):  # time after
        query = query.where(func.date(Mail.time) >= filters['af'])
    # if filters.get('ke'):  # keyword
    #     query = query.where(Mail.keyword.like(f"%{filters['ke']}%"))
    if filters.get('ke'):  # keyword
        if filters.get('se'):
            word_set_en = get_lemmas_en(filters['ke'])
            word_set_jpn = get_lemmas_jpn(filters['ke'])
            word_set = '|'.join([word_set_en, word_set_jpn])
        else:
            word_set = filters['ke']
        query = query.where(Mail.keyword.regexp_match(f"({word_set})"))
    if filters.get('id') is not None:
        query = query.where(Mail.id == filters['id'])
    return query


def delete_mail_with_id(session, mail_id):
    session.query(Mail).filter(Mail.id == mail_id).delete()
    session.commit()


def update_mail_keyword_with_id(session, mail_id, new_keyword):
    session.query(Mail).filter(Mail.id == mail_id).update({Mail.keyword: new_keyword})
    session.commit()


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
        # insert_into_tables(session, data)
        # print_all_table(session)

        # mails = session.execute(text("select * from mails")).all()
        # print(mails)

        # sql_text = '''
        # SELECT su.name sender_name, su.email_address sender_email_address,
        #     ru.name recipient_name, ru.email_address recipient_email_address,
        #     m.mail_server_id, m.subject, m.keyword, m.time
        # FROM mails m
        # JOIN users su
        # ON m.sender = su.id
        # JOIN users ru
        # ON m.recipient = ru.id
        # '''
        # mails = session.execute(text(sql_text)).all()
        # print(mails)

        # userR = aliased(User, name="userR")
        # userS = aliased(User, name="userS")
        # statement = \
        #     select(userS.name, userS.email_address, userR.name, userR.email_address,
        #            Mail.mail_server_id, Mail.subject, Mail.keyword, Mail.time)\
        #     .join(userS, Mail.sender_user).join(userR, Mail.recipient_user)
        # statement = statement.where(userS.email_address == 'cyrilcao28@gmail.com')
        # statement = statement.where(userS.name == 'yilei CAO')
        # statement = statement.where(func.date(Mail.time) <= '2023-11-23')
        # statement = statement.where(Mail.keyword.like('%thank%'))
        statement = select(Mail)
        print(statement)
        rows = session.execute(statement).all()
        print(rows)
