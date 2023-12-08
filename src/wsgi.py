from flask import Flask, render_template, request, url_for, flash, \
    redirect, escape, session
from markupsafe import Markup
from sqlalchemy import text, select
from sqlalchemy.orm import Session
from src.db_func import insert_into_tables, print_all_table, build_select_statement, delete_mail_with_id, \
    update_mail_keyword_with_id, get_user, insert_user, change_mail_is_public_status_with_id, get_mail_owner_from_id
from src.gmail_func import gmail_authenticate, search_messages, generate_metadata_from_msgs, data_extract_keyword, \
    get_text_from_server
from database import db_session, init_db, engine
from src.keybert_func import extract_keyword
from functools import wraps

app = Flask(__name__)

# config
app.secret_key = 'my precious'


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.', 'warning')
            return redirect(url_for('home'))
    return wrap


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/', methods=['GET'])
def home():
    if session.get('logged_in') is None:
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        with Session(engine) as db_session:
            account = get_user(db_session, username, password)
        if account:
            session['logged_in'] = True
            session['id'] = account.id
            session['username'] = account.user_name
            flash('Logged in successfully !', 'success')
            return redirect(url_for('mail_list'))
        else:
            flash('Incorrect username / password !', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You were logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST' \
            and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        with Session(engine) as db_session:
            status = insert_user(db_session, username, password)
            if status:
                flash('You have successfully registered !', 'success')
                return redirect(url_for('login'))
            else:
                flash('Account already exists !', 'warning')
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html')


@app.route('/greet')
def greet():  # http://127.0.0.1:8000/greet?name=aa
    name = request.args['name']
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <h1>Hi {}</h1>
    </body>
    </html>'''.format(escape(name))


@app.route('/load_mails', methods=('GET', 'POST'))
@login_required
def load_mails():
    if request.method == 'POST':
        if 'get-emails' in request.form:
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
            return redirect(f'/raw_mail_list/{encoded_query}/1')
    return render_template('load_mails.html')


@app.route('/raw_mail_list/<encoded_query>/<page_num>', methods=('GET', 'POST'))
@login_required
def raw_mail_list(encoded_query, page_num):
    message_per_page = 10
    page_num = int(page_num)
    query = encoded_query.replace('0x20', ' ')
    service = gmail_authenticate(session['username'])
    msg_ids = search_messages(service, query)
    # print(f"Found {len(results)} results.")
    is_end = False
    total_num = len(msg_ids)
    if total_num <= message_per_page * page_num:
        is_end = True
    msg_ids = msg_ids[message_per_page * (page_num - 1):message_per_page * page_num]
    metadata = generate_metadata_from_msgs(service, msg_ids)

    if request.method == 'GET':
        flash(f'Found {total_num} matching mails, now showing mails from {message_per_page * (page_num - 1) + 1} to '
              f'{message_per_page * (page_num - 1) + len(msg_ids)}', 'info')
        return render_template('raw_mail_list.html', emails=metadata)
    if request.method == 'POST':
        if 'confirm-emails' in request.form:
            # for each email matched, read it (output plain/text to console & save HTML and attachments)
            inserted_data = []
            for name in list(request.form.keys()):
                if name.startswith('mail'):
                    num = int(name[4:])
                    row = metadata[num]
                    row.pop('id')
                    inserted_data.append(row)
            get_text_from_server(service, inserted_data)
            data_extract_keyword(inserted_data)
            with Session(engine) as db_session:
                num_succeed = insert_into_tables(db_session, inserted_data)
                num_failed = len(inserted_data) - num_succeed
                flash(f"You've successfully added {num_succeed} new mails! {num_failed} mails already in DB.", 'success')
                # info, error, warning
                if is_end:
                    return redirect(url_for('load_mails'))
                else:
                    return redirect(f'/raw_mail_list/{encoded_query}>/{page_num+1}')


def mail_search_text(sql_request):
    with Session(engine) as db_session:
        mails = db_session.execute(text(sql_request)).fetchall()
    return mails


def mail_search_statement(query):
    with Session(engine) as db_session:
        mails = db_session.execute(query).fetchall()
    return mails


@app.route('/mail_list_text', defaults={'encoded_sql': None}, methods=['GET', 'POST'])
@app.route('/mail_list_text/<encoded_sql>/', methods=('GET', 'POST'))
@login_required
def mail_list_text(encoded_sql):
    if request.method == 'POST':
        sql_request = request.form['sql_request']
        # encoded_sql = base64.b64encode(bytes(sql_request, 'utf-8'))
        encoded_sql = sql_request.replace(' ', '1')
        return redirect(url_for('mail_list', encoded_sql=encoded_sql))
    # sql_request = encoded_sql.decode('utf-8')
    if encoded_sql is None:
        mails = []
    else:
        sql_request = encoded_sql.replace('1', ' ')
        mails = mail_search_text(sql_request)
    return render_template('mail_list_text.html', emails=mails)


@app.route('/mail_list/', methods=('GET', 'POST'))
@login_required
def mail_list():
    if request.method == 'POST':
        keyword = request.form['keyword']
        date_after = request.form['date_after']
        date_before = request.form['date_before']
        email_from = request.form['email_from']
        email_to = request.form['email_to']
        is_kw_semantic = request.form.get('is_kw_semantic')
        is_kw_jpn = request.form.get('is_kw_jpn')
        email_thread = request.form.get('email_thread')
        email_subject = request.form.get('email_subject')
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
        query = query[:-1]
        return redirect(f'/mail_list/{query}')
    filters = request.args.to_dict()
    query = build_select_statement(filters)
    mails = mail_search_statement(query)
    return render_template('mail_list.html', emails=mails, request=filters)


@app.route('/view_mail/<mail_id>', methods=('GET', 'POST'))
@login_required
def view_mail(mail_id):
    if request.method == 'POST':
        if 'edit_keyword' in request.form:
            new_keyword = request.form['new_keyword']
            if len(new_keyword) > 0:
                with Session(engine) as db_session:
                    update_mail_keyword_with_id(db_session, mail_id, new_keyword)
                    flash(f'Mail {mail_id} keyword updated', 'success')
                return redirect(url_for('view_mail', mail_id=mail_id))
    mail_id = int(mail_id)
    filters = {'id': mail_id}
    query = build_select_statement(filters)
    mail = mail_search_statement(query)
    if not mail:
        flash("You don't have access to this mail!", 'danger')
        return redirect(url_for('mail_list'))
    mail = mail[0]
    mail_server_id = mail[4]  # mail_server_id
    with Session(engine) as db_session:
        mail_owner = get_mail_owner_from_id(db_session, mail_id)
    service = gmail_authenticate(mail_owner)
    plain_text = get_text_from_server(service, [{'mail_server_id': mail_server_id}])[0]['text']
    keywords = mail[6]
    params = {}
    if request.method == 'POST' and 'generate_keyword' in request.form:

        kw_len_fr = request.form['range_from'] or 1
        kw_len_to = request.form['range_to'] or 3
        diversity = request.form['diversity'] or 0.5
        kw_num = request.form['number'] or 5
        key_word = extract_keyword(plain_text, kw_len_fr=int(kw_len_fr), kw_len_to=int(kw_len_to),
                                   diversity=float(diversity), kw_num=int(kw_num))
        keywords = ', '.join([i[0] for i in key_word])
        params = request.form.to_dict()
        params['keyword'] = keywords
    s_kw = keywords.replace(',', ' ').split()
    for keyword in keywords.replace(',', ' ').split():
        keyword = keyword.strip()
        for word in (keyword, keyword.upper(), keyword.capitalize()):
            plain_text = plain_text.replace(f'{word}', f'<mark style="background-color:burlywood;">{word}</mark>')
    plain_text = Markup(plain_text)
    is_owner = mail_owner == session['username']
    return render_template('view_mail.html', data=mail, text=plain_text, kw_params=params, s_kw=s_kw, is_owner=is_owner)


@app.route('/delete_mail/<mail_id>', methods=['POST'])
@login_required
def delete_mail(mail_id):
    if request.method == 'POST':
        if 'delete_mail' in request.form:
            with Session(engine) as db_session:
                if delete_mail_with_id(db_session, mail_id):
                    flash(f'Mail {mail_id} successfully removed', 'success')
            return redirect(url_for('mail_list'))
        elif 'share_mail' in request.form:
            with Session(engine) as db_session:
                is_public = change_mail_is_public_status_with_id(db_session, mail_id)
                if is_public is not None:
                    if is_public:
                        flash(f'Successfully share Mail {mail_id}', 'success')
                    else:
                        flash(f'Successfully make Mail {mail_id} private', 'success')
            return redirect(url_for('view_mail', mail_id=mail_id))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    init_db()
    app.run(host='0.0.0.0', port='8001', debug=True)
