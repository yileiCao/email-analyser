from datetime import datetime

import pytest
from sqlalchemy import create_engine, insert, select, func
from sqlalchemy.orm import sessionmaker

from src.db_func import get_user_id, insert_into_tables, print_all_table
from src.db_models import Base, User, Mail


@pytest.fixture
def generate_session():
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def generate_user_data(session):
    data = [{'name': 'aa', 'email_address': 'aa@email.com'},
            {'name': 'bb', 'email_address': 'bb@bmail.com'}]
    session.execute(insert(User), data)
    session.commit()


def test_insert_into_tables(generate_session):
    data = [
        {'mail_server_id': '18bfd1199e673cc7', 'sender': '"LEGO® Shop" <Noreply@t.crm.lego.com>',
         'recipient': '<cyrilcao28@gmail.com>', 'keyword': '受付完了！ 行健様のご注文が確定しました。',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')},
        {'mail_server_id': '18bf1a0b42cfce45', 'sender': 'LinkedIn <messages-noreply@linkedin.com>',
         'keyword': ' Yilei, add Pankaj Gawande - Solution Architect - SAP BRIM at Acuiti Labs',
         'recipient': 'Yilei Cao <cyrilcao28@gmail.com>',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')}]
    insert_into_tables(generate_session, data)
    mail_result = generate_session.execute(select(Mail.sender, Mail.recipient))
    assert len(list(mail_result)) == 2
    for row in mail_result:
        sender_id, recipient_id = row
        assert isinstance(sender_id, int)
        assert isinstance(recipient_id, int)
    user_count = generate_session.execute(select(func.count(User.id))).scalar()
    assert user_count == 4


def test_get_user_id(generate_session):
    generate_user_data(generate_session)
    user_info1 = '"aa "<aa@email.com>'
    user_info2 = '"bb "<aa@email.com>'
    result1 = get_user_id(generate_session, user_info1)
    assert (result1 == 1)
    result2 = get_user_id(generate_session, user_info2)
    assert (result2 == 3)

