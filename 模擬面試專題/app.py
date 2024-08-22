from flask import Flask, redirect, url_for, render_template
import auth
import main

app = Flask(__name__)

DATABASE = './flaskr.db'
SECRET_KEY = 'your_secret_key'
DEBUG = True


app = Flask(__name__)
app.config.from_object(__name__)
app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)


@app.route('/home') #舊的首頁
def home():
    return render_template('home.html')

@app.route('/') #新的首頁，用這個
def index():
    return render_template('index.html')


@app.route('/vision') #未來展望
def vision():
    return render_template('our_vision.html')

@app.route('/about') #關於我們
def about():
    return render_template('about.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    return redirect(url_for('auth.login'))




if __name__ == '__main__':
    app.run(debug=True)
