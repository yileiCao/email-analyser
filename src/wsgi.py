from flask import Flask, render_template, request, url_for, flash, redirect, escape
from sqlalchemy import text, select
from sqlalchemy.orm import Session
import base64
from src.db_func import insert_into_tables, print_all_table
from src.gmail_func import gmail_authenticate, search_messages, generate_data_from_msgs
from database import db_session, init_db, engine

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def home():
    # conn = get_db_connection()
    # posts = conn.execute('SELECT * FROM posts').fetchall()
    # conn.close()
    return render_template('home.html')


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
def load_mails():
    if request.method == 'POST':
        keyword = request.form['keyword']
        date_after = request.form['date_after']
        date_before = request.form['date_before']
        email_from = request.form['email_from']
        email_to = request.form['email_to']

        query = ""
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

        results = search_messages(service, query)
        print(f"Found {len(results)} results.")
        # for each email matched, read it (output plain/text to console & save HTML and attachments)
        data = generate_data_from_msgs(service, results)
        with Session(engine) as session:
            insert_into_tables(session, data)
            print_all_table(session)

    return render_template('load_mails.html')


@app.route('/search_mails')
def search_mails():
    return redirect(url_for('mail_list', encoded_sql='None'))


def mail_search(sql_request):
    with Session(engine) as session:
        mails = session.execute(text(sql_request)).fetchall()
    return mails


@app.route('/mail_list/<encoded_sql>/', methods=('GET', 'POST'))
def mail_list(encoded_sql):
    if request.method == 'POST':
        sql_request = request.form['sql_request']
        # encoded_sql = base64.b64encode(bytes(sql_request, 'utf-8'))
        encoded_sql = sql_request.replace(' ', '1')
        return redirect(url_for('mail_list', encoded_sql=encoded_sql))
    # sql_request = encoded_sql.decode('utf-8')
    if encoded_sql == "None":
        mails = []
    else:
        sql_request = encoded_sql.replace('1', ' ')
        mails = mail_search(sql_request)
    return render_template('mail_list.html', emails=mails)


if __name__ == '__main__':
    init_db()
    service = gmail_authenticate()
    app.run(host='0.0.0.0', port='8000', debug=True)