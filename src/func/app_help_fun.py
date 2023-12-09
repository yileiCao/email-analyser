from markupsafe import Markup

from src.func.keybert_func import extract_keyword


def build_raw_mail_list_encoded_query(request):
    keyword = request.form['keyword']
    date_after = request.form['date_after']
    date_before = request.form['date_before']
    email_from = request.form['email_from']
    email_to = request.form['email_to']
    filter_text = request.form['filter_text']
    query = " "
    if keyword:
        query += f"{keyword} "
    if date_after:
        query += f"after:{date_after} "
    if date_before:
        query += f"before:{date_before} "
    if email_from:
        query += f"from:{email_from} "
    if email_to:
        query += f"to:{email_to} "
    if filter_text:
        query += filter_text
    encoded_query = query.replace(' ', '0x20')
    return encoded_query


def mail_search_statement(db_session, query):
    mails = db_session.execute(query).fetchall()
    return mails


def build_mail_list_query(request):
    keyword = request.form['keyword']
    date_after = request.form['date_after']
    date_before = request.form['date_before']
    email_from = request.form['email_from']
    email_to = request.form['email_to']
    is_kw_semantic = request.form.get('is_kw_semantic')
    is_kw_jpn = request.form.get('is_kw_jpn')
    email_thread = request.form.get('email_thread')
    email_subject = request.form.get('email_subject')
    email_status = request.form.get('mail_status')
    query = "?"
    if email_from:
        query += f"fr={email_from}&"
    if email_to:
        query += f"to={email_to}&"
    if date_before:
        query += f"be={date_before}&"
    if date_after:
        query += f"af={date_after}&"
    if keyword:
        query += f"ke={keyword}&"
    if is_kw_semantic:
        query += f"se={is_kw_semantic}&"
    if is_kw_jpn:
        query += f"jpn={is_kw_jpn}&"
    if email_thread:
        query += f"et={email_thread}&"
    if email_subject:
        query += f"sbj={email_subject}&"
    if email_status:
        query += f"st={email_status}&"
    query = query[:-1]
    return query


def keyword_generation_params(request, plain_text):
    kw_len_fr = request.form['range_from'] or 1
    kw_len_to = request.form['range_to'] or 1
    diversity = request.form['diversity'] or 0.5
    kw_num = request.form['number'] or 10
    key_word = extract_keyword(plain_text, kw_len_fr=int(kw_len_fr), kw_len_to=int(kw_len_to),
                               diversity=float(diversity), kw_num=int(kw_num))
    keywords = ', '.join([i[0] for i in key_word])
    params = request.form.to_dict()
    params['keyword'] = keywords
    return params


def highlight_keyword_in_text(plain_text, keywords):
    for keyword in set(keywords.replace(',', ' ').split()):
        keyword = keyword.strip()
        for word in (keyword, keyword.upper(), keyword.capitalize()):
            plain_text = plain_text.replace(f'{word}', f'<mark style="background-color:burlywood;">{word}</mark>')
    return Markup(plain_text)


