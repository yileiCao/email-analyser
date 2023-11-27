from datetime import datetime

import pytest
from sqlalchemy import create_engine, insert, select, func
from sqlalchemy.orm import sessionmaker

from src.db_func import get_user_id, insert_into_tables, print_all_table, build_select_statement
from src.db_models import Base, User, Mail


@pytest.fixture
def generate_session():
    # engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
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


def generate_email_data(session):
    data = [{'sender': 'test <test@gmail.com>', 'recipient': 'yilei <cyrilcao28@gmail.com>',
             'time': datetime(2023, 11, 24, 18, 6, 17), 'mail_server_id': '18c00947079add6d',
             'keyword': 'recruit rutilea jobcan, dear hr team, seminar nov 18th, patience appreciate registering, '
                        'selection results notified'},
            {'sender': 'test <test@gmail.com>', 'recipient': 'yilei <cyrilcao28@gmail.com>',
             'time': datetime(2023, 11, 18, 14, 35, 47), 'mail_server_id': '18be0ed92c2d313a',
            'keyword': '株式会社rutilea 採用担当 recruit, briefing conducted google, meet time required, '
                       'thank arrangement seminar, jobcan ats jp'},
            {'sender': 'yilei <cyrilcao28@gmail.com>', 'recipient': 'test <test@gmail.com>',
            'time': datetime(2023, 11, 17, 13, 6, 57), 'mail_server_id': '18bdb75e2eb7d2dd',
             'keyword': 'schedule tomorrow seminar, workshop send, '
                       'sincerely rutilea hr, received 1st task, jobcan ats jp'},
            {'sender': 'yilei <cyrilcao28@gmail.com>', 'recipient': 'test2 <test@gmail.com>',
             'time': datetime(2023, 11, 14, 16, 30, 30), 'mail_server_id': '18bccbd2b9cc9308',
             'keyword': 'recruiter rutilea thank, deadline frist task, submit ideas ai, '
                        'selection process check, fair held osaka'}]
    insert_into_tables(session, data)


def test_insert_into_tables(generate_session):
    data = [
        {'mail_server_id': '18bfd1199e673cc7', 'sender': '"LEGO® Shop" <Noreply@t.crm.lego.com>',
         'recipient': '<cyrilcao28@gmail.com>', 'keyword': '受付完了！ 行健様のご注文が確定しました。',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')},
        {'mail_server_id': '18bf1a0b42cfce45', 'sender': 'LinkedIn <messages-noreply@linkedin.com>',
         'keyword': ' Yilei, add Pankaj Gawande - Solution Architect - SAP BRIM at Acuiti Labs',
         'recipient': 'Yilei Cao <cyrilcao28@gmail.com>',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')},
        {'mail_server_id': '18bf1a0b42cfce45', 'sender': 'LinkedIn <messages-noreply@linkedin.com>',
         'keyword': ' Yilei, add Pankaj Gawande - Solution Architect - SAP BRIM at Acuiti Labs',
         'recipient': 'Yilei Cao <cyrilcao28@gmail.com>',
         'time': datetime.strptime('Thu, 23 Nov 2023 10:44:27 -0600', '%a, %d %b %Y %H:%M:%S %z')}
    ]
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


def test_build_select_statement(generate_session):
    generate_email_data(generate_session)
    filters1 = {}
    query1 = build_select_statement(filters1)
    rows1 = generate_session.execute(query1).all()
    assert len(rows1) == 4
    filters2 = {"sender_email": "cyrilcao28@gmail.com"}
    query2 = build_select_statement(filters2)
    rows2 = generate_session.execute(query2).all()
    assert len(rows2) == 2
    filters3 = {"date_before": '2023-11-23'}
    query3 = build_select_statement(filters3)
    rows3 = generate_session.execute(query3).all()
    assert len(rows3) == 3
    filters4 = {"keyword": 'task'}
    query4 = build_select_statement(filters4)
    rows4 = generate_session.execute(query4).all()
    assert len(rows4) == 2
