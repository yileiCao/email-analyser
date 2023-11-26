from src.gmail_func import search_messages, gmail_authenticate


def test_gmail_authenticate():
    pass


def test_search_messages():
    service = gmail_authenticate()
    query1 = 'in:inbox is:unread'
    result1 = search_messages(service, query1, get_all=False)
    assert len(result1) != 0
    query2 = 'has:attachment is:important'
    result2 = search_messages(service, query2, get_all=False)
    assert len(result2) != 0
    query3 = 'after:2023/11/01 before:2023/12/01'
    result3 = search_messages(service, query3, get_all=False)
    assert len(result3) != 0
    query4 = 'from:LEGO®Shop to:me'
    result4 = search_messages(service, query4, get_all=False)
    assert len(result4) != 0
    query5 = 'from:recruit@rutilea.jobcan-ats.jp subject:task'
    result5 = search_messages(service, query5, get_all=False)
    assert len(result5) != 0




