from src.myapp import app

app.config.from_object('src.config.Config')
# app.config.from_object('src.config.DbConfig')
# app.run(host='0.0.0.0', port='8001')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8001')