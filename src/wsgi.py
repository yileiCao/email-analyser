from flask import Flask, render_template, request, url_for, flash, redirect, escape

from src.db_func import insert_into_tables, print_all_table
from src.gmail_func import gmail_authenticate, search_messages, generate_data_from_msgs
from database import db_session, init_db, engine

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    # conn = get_db_connection()
    # posts = conn.execute('SELECT * FROM posts').fetchall()
    # conn.close()
    return render_template('index.html')


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
        # data = generate_data_from_msgs(service, results)
        # with engine.connect() as conn:
        #     insert_into_tables(conn, data)
        #     print_all_table(conn)

    return render_template('load_mails.html')


if __name__ == '__main__':
    init_db()
    service = gmail_authenticate()
    app.run(host='0.0.0.0', port='8000', debug=True)