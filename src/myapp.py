from flask import Flask, render_template, request, url_for, flash, redirect, session
from sqlalchemy.orm import Session

from src.func.app_help_fun import build_raw_mail_list_encoded_query, mail_search_statement, build_mail_list_query, \
    keyword_generation_params, highlight_keyword_in_text
from src.func.db_func import insert_into_tables, build_select_statement, delete_mail_with_id, \
    update_mail_keyword_with_id, get_user, insert_user, change_mail_is_public_status_with_id, get_mail_owner_from_id
from src.func.gmail_func import gmail_authenticate, search_messages, generate_metadata_from_msgs, \
    data_extract_keyword, get_text_from_server
from src.database import engine
from functools import wraps

app = Flask(__name__)


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


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username') is not None:
        flash('You have already logged in.', 'info')
        return redirect(url_for('mail_list'))
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' \
            and 'username' in request.form and 'password' in request.form \
            and request.form['username'] and request.form['password']:
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
        flash('Please fill out the form !', 'warning')
    return render_template('register.html')


@app.route('/load_mails', methods=('GET', 'POST'))
@login_required
def load_mails():
    if request.method == 'POST':
        if 'get-emails' in request.form:
            encoded_query = build_raw_mail_list_encoded_query(request)
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
                flash(f"You've successfully added {num_succeed} new mails! "
                      f"{num_failed} mails already in DB.", 'success')
                # info, error, warning
                if is_end:
                    return redirect(url_for('load_mails'))
                else:
                    return redirect(f'/raw_mail_list/{encoded_query}>/{page_num+1}')


@app.route('/mail_list/', methods=('GET', 'POST'))
@login_required
def mail_list():
    if request.method == 'POST':
        url_query = build_mail_list_query(request)
        return redirect(f'/mail_list/{url_query}')
    filters = request.args.to_dict()
    db_query = build_select_statement(filters)
    with Session(engine) as db_session:
        mails = mail_search_statement(db_session, db_query)
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
    db_query = build_select_statement(filters)
    with Session(engine) as db_session:
        mail = mail_search_statement(db_session, db_query)
        mail_owner = get_mail_owner_from_id(db_session, mail_id)
    if not mail:
        flash("You don't have access to this mail!", 'danger')
        return redirect(url_for('mail_list'))
    mail = mail[0]
    mail_server_id = mail[4]  # mail_server_id
    service = gmail_authenticate(mail_owner)
    plain_text = get_text_from_server(service, [{'mail_server_id': mail_server_id}])[0]['text']
    keywords = mail[6]

    params = {}
    if request.method == 'POST' and 'generate_keyword' in request.form:
        params = keyword_generation_params(request, plain_text)
    split_kw = keywords.replace(',', ' ').replace(';', ' ').split()
    plain_text = plain_text.replace('<', '').replace('>', '')
    highlighted_text = highlight_keyword_in_text(plain_text, keywords)
    is_owner = mail_owner == session['username']
    return render_template('view_mail.html', data=mail, text=highlighted_text,
                           kw_params=params, s_kw=split_kw, is_owner=is_owner)


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


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', e=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('500.html', e=e), 500


@app.errorhandler(Exception)
def internal_server_error(e):
    return render_template('error.html', e=e)
