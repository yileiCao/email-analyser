
from sqlalchemy import insert, select, func, or_, and_
from sqlalchemy.orm import aliased
from werkzeug.security import check_password_hash, generate_password_hash

from src.db_models import Mail, Customer, User
from src.func.wordnet_func import get_lemmas_en, get_lemmas_jpn
from flask import session


def get_user(db_session, username, password):
    user_record = db_session.execute(select(User.id, User.user_name, User.password).where(
        User.user_name == username)).first()
    if user_record and check_password_hash(user_record.password, password):
        return user_record
    return None


def insert_user(db_session, username, password):
    if db_session.execute(select(User.id).where(
            User.user_name == username)).first():
        return False
    else:
        db_session.execute(insert(User).values(user_name=username, password=generate_password_hash(password)))
        db_session.commit()
        return True


def insert_into_tables(db_session, mail_data):
    num_succeed = len(mail_data)
    for mail_info in mail_data:
        mail_info['sender'] = get_user_id(db_session, mail_info['sender'])
        mail_info['recipient'] = get_user_id(db_session, mail_info['recipient'])
        mail_info['owner'] = session['id']
    if mail_data:
        for mail in mail_data:
            if db_session.execute(select(Mail.id).where(
                    Mail.mail_server_id == mail['mail_server_id'])).all():
                num_succeed -= 1
                continue
            db_session.merge(Mail(**mail))
        db_session.commit()
    return num_succeed


def get_user_id(db_session, user_info):
    try:
        name, addr = user_info.split('<')
    except ValueError:
        name, addr = None, user_info
    if isinstance(name, str):
        name = name.strip('\'" ')
    addr = addr.strip('\'" <>')
    id = db_session.execute(select(Customer.id).where(
        Customer.email_address == addr,
        Customer.name == name)).scalar()
    if not id:  # not included in user db, need new insertion
        id = db_session.execute(insert(Customer).values(email_address=addr, name=name).returning(
            Customer.id)).scalar()
        db_session.commit()
    return id


def print_all_table(db_session):
    stmt = select(Customer)
    for user in db_session.execute(stmt):
        print(user)
    stmt = select(Mail)
    for mail in db_session.execute(stmt):
        print(mail)


def build_select_statement(filters):
    customerR = aliased(Customer, name="customerR")
    customerS = aliased(Customer, name="customerS")
    query = \
        select(customerS.name, customerS.email_address, customerR.name, customerR.email_address,
               Mail.mail_server_id, Mail.subject, Mail.keyword,
               Mail.time, Mail.id, Mail.mail_thread_id, Mail.is_public) \
            .join(customerS, Mail.sender_user).join(customerR, Mail.recipient_user) \
            .order_by(Mail.time.desc())
    if filters.get("fr"):  # sender email_address
        query = query.where(customerS.email_address == filters["fr"])
    if filters.get("to"):  # recipient email_address
        query = query.where(customerR.email_address == filters["to"])
    if filters.get('be'):  # time before
        query = query.where(func.date(Mail.time) <= filters['be'])
    if filters.get('af'):  # time after
        query = query.where(func.date(Mail.time) >= filters['af'])
    if filters.get('sbj'):  # email_subject
        query = query.where(Mail.subject.like(f"%{filters['sbj']}%"))
    if filters.get('ke'):  # keyword
        if filters.get('se'):  # semantic search
            word_set = get_lemmas_en(filters['ke'])
            if filters.get('jpn'):
                word_set_jpn = get_lemmas_jpn(filters['ke'])
                word_set = '|'.join([word_set, word_set_jpn])
        else:
            word_set = filters['ke']
        query = query.where(Mail.keyword.regexp_match(f"({word_set})"))
    if filters.get('id') is not None:
        query = query.where(Mail.id == filters['id'])
    if filters.get('et'):  # email_thread
        query = query.where(Mail.mail_thread_id == filters['et'])

    mail_status = filters.get('st', 'all')
    if mail_status == 'own':
        query = query.where(Mail.owner == session['id'])
    elif mail_status == 'share':
        query = query.where(and_(Mail.is_public == True, Mail.owner != session['id']))
    else:  # mail_status == 'all
        query = query.where(or_(Mail.is_public == True, Mail.owner == session['id']))
    return query


def delete_mail_with_id(db_session, mail_id):
    mail_owner = db_session.execute(db_session.query(User.user_name).filter(User.id == Mail.owner,
                                                                            Mail.id == mail_id)).scalar()
    if mail_owner == session['username']:
        db_session.query(Mail).filter(Mail.id == mail_id).delete()
        db_session.commit()
        return True
    return False


def change_mail_is_public_status_with_id(db_session, mail_id):
    is_public = db_session.execute(db_session.query(Mail.is_public).filter(Mail.id == mail_id)).scalar()
    mail_owner = db_session.execute(db_session.query(User.user_name).filter(User.id == Mail.owner,
                                                                            Mail.id == mail_id)).scalar()
    if mail_owner == session['username']:
        db_session.query(Mail).filter(Mail.id == mail_id).update({Mail.is_public: not is_public})
        db_session.commit()
        return not is_public


def get_mail_owner_from_id(db_session, mail_id):
    return db_session.execute(db_session.query(User.user_name).filter(User.id == Mail.owner, Mail.id == mail_id)).scalar()


def update_mail_keyword_with_id(db_session, mail_id, new_keyword):
    mail_owner = db_session.execute(db_session.query(User.user_name).filter(User.id == Mail.owner,
                                                                            Mail.id == mail_id)).scalar()
    if mail_owner == session['username']:
        db_session.query(Mail).filter(Mail.id == mail_id).update({Mail.keyword: new_keyword})
        db_session.commit()
        return True
    return False

