from src.app import app

app.config.from_object('config.Config')
# app.config.from_object('config.DbConfig')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8001')