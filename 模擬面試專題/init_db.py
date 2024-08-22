import sqlite3
from flask import Flask

# configuration
DATABASE = './flaskr.db'


app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    with connect_db() as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


if __name__ == '__main__':
    init_db()