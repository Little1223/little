from flask import Flask, render_template, jsonify, request, session, redirect, url_for,Blueprint, flash, g
import openai
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging
import auth
import functools
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import re

# 加載 .env 檔案中的環境變數
load_dotenv()

bp = Blueprint('main', __name__, url_prefix='/main')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

CORS(app)  # 啟用 CORS

# 設置日誌
logging.basicConfig(level=logging.DEBUG)

# 從環境變數中獲取 OpenAI API 密鑰
openai.api_key = os.getenv('OPENAI_API_KEY')

@bp.route('/', methods=('GET', 'POST'))#首頁
@auth.login_required 
def form():
    return render_template('form.html')

@bp.route('/index')
def index():
    return render_template('index.html')


# @bp.route('/end_session', methods=['GET'])
# def end_session():
#     return redirect(url_for('index.html'))


@bp.route('/submit', methods=['GET']) #form.html 裡的表單get到session.html
def submit():

    name = request.args.get('name')
    gender = request.args.get('gender')
    email = request.args.get('email')
    age = request.args.get('age')
    tenure = request.args.get('tenure')
    job_description = request.args.get('job_description')
    job_detail = request.args.get('job_detail')
    experience = request.args.get('experience')
    skills = request.args.get('skills')


    if request.method == 'GET':
        db = get_db()

        name = str(name)
        gender = str(gender)
        email = str(email)
        age = int(age)
        tenure = int(tenure)
        job_description = str(job_description)
        job_detail = str(job_detail)
        experience = str(experience)
        skills = str(skills)

        print('name---------',name)
        print('age---------',age)
        print('job_description---------',job_description)
        print('job_detail---------',job_detail)
        print('tenure---------',tenure)


        db.execute(
            "UPDATE user SET name = ? WHERE id = ?", (name, session['user_id'])
        )
        db.execute(
            "UPDATE user SET gender = ? WHERE id = ?", (gender, session['user_id'])
        )
        db.execute(
            "UPDATE user SET email = ? WHERE id = ?", (email, session['user_id'])
        )
        db.execute(
            "UPDATE user SET age = ? WHERE id = ?", (age, session['user_id'])
        )
        db.execute(
            "UPDATE user SET tenure = ? WHERE id = ?", (tenure, session['user_id'])
        )
        db.execute(
            "UPDATE user SET job_description = ? WHERE id = ?", (job_description, session['user_id'])
        )
        db.execute(
            "UPDATE user SET job_detail = ? WHERE id = ?", (job_detail, session['user_id'])
        )
        db.execute(
            "UPDATE user SET experience = ? WHERE id = ?", (experience, session['user_id'])
        )
        db.execute(
            "UPDATE user SET skills = ? WHERE id = ?", (skills, session['user_id'])
        )

        db.commit()

    return render_template('session.html', name=name, gender=gender, age=age, tenure=tenure, email=email, job_detail=job_detail, job_description=job_description, experience=experience, skills=skills)



# 用來存儲5個數字的全域陣列
scores = []

@bp.route('/generate_response', methods=['POST'])  # openai api 
def generate_response():
    global scores  # 指明使用全域的 scores 變數
    try:
        data = request.get_json()
        conversation = data.get('conversation')

        if not conversation:
            return jsonify({"error": "未提供對話記錄"}), 400

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=300,
            temperature=0.7
        )
    # ------------- 0722edit --------------
        chat_response = response.choices[0].message.content
        matches = re.findall(r'(\d+)分', chat_response)
       
        if matches:
            scores = [int(match) for match in matches[:5]]  # 將找到的數字轉換為整數並存入 scores，最多抓5個
            if len(scores) >= 5:
                score1, score2, score3, score4, score5 = scores

                error = None
                try:
                    score1 = int(score1) if score1 is not None else None
                    score2 = int(score2) if score2 is not None else None
                    score3 = int(score3) if score3 is not None else None
                    score4 = int(score4) if score4 is not None else None
                    score5 = int(score5) if score5 is not None else None
                except (ValueError, TypeError):
                    error = 'All scores must be integers.'
                if error is None:
                    valid_scores = [score for score in [score1, score2, score3, score4, score5] if score is not None]
                if valid_scores:
                    score6 = sum(valid_scores) / len(valid_scores)

                    db = get_db()
                    db.execute("UPDATE user SET score1 = ?, score2 = ?, score3 = ?, score4 = ?, score5 = ?, score6 = ? WHERE id = ?", 
                               (score1, score2, score3, score4, score5, score6, session['user_id']))
                    db.commit()
        print(scores)  # 這裡你可以看到所有存入的數字
        return jsonify({"response": chat_response})
    # ------------- 0722edit --------------
    except openai.error.OpenAIError as e:
        return jsonify({"error": "OpenAI API 錯誤: " + str(e)}), 500
    except Exception as e:
        return jsonify({"error": "伺服器錯誤: " + str(e)}), 500
    
    
@bp.route('/report', methods=['GET'])
def report():
    db = get_db()
    error = None

    try:
        user_id = session.get('user_id')
        if not user_id:
            error = "User ID not found in session."
            raise Exception(error)

        scores = db.execute(
            "SELECT score1, score2, score3, score4, score5, score6 FROM user WHERE id = ?", 
            (user_id,)
        ).fetchone()

        if not scores:
            error = "Failed to retrieve scores for the current user."
            raise Exception(error)

        score1, score2, score3, score4, score5, score6 = scores

        grades = db.execute(
            "SELECT score1, score2, score3, score4, score5, score6 FROM user"
        ).fetchall()

        scores_list = {i: [row[f'score{i}'] for row in grades if row[f'score{i}'] is not None] for i in range(1, 7)}

        average_scores = {i: (sum(scores_list[i]) / len(scores_list[i])) if scores_list[i] else 0 for i in range(1, 7)}

        current_job_description = db.execute(
            "SELECT job_description FROM user WHERE id = ?", 
            (user_id,)
        ).fetchone()
        current_user_gender = db.execute(
            "SELECT gender FROM user WHERE id = ?", 
            (user_id,)
        ).fetchone()

        if current_user_gender:
            gender_input = current_user_gender['gender']
            else_gender_input = '女' if gender_input == '男' else '男'
        else:
            gender_input = None
            error = "Failed to retrieve current user's gender."
            raise Exception(error)

        score6_value = score6
        if score6_value is None:
            error = "Failed to retrieve score6."
            raise Exception(error)

        total_users = db.execute("SELECT score6 FROM user").fetchall()
        score_list = [row['score6'] for row in total_users if row['score6'] is not None]
        sorted_scores = sorted(score_list + [score6_value])
        rank = sorted_scores.index(score6_value) + 1
        score6_rank_percentage = ((len(score_list) - rank + 1) / len(score_list)) * 100
        else_score6_rank_percentage = 100 - score6_rank_percentage

        job_description_input = current_job_description['job_description'] if current_job_description else None
        if job_description_input is None:
            error = "Failed to retrieve current user's job description."
            raise Exception(error)

        job_description = db.execute("SELECT job_description FROM user").fetchall()
        job_description_list = [row['job_description'] for row in job_description]
        total_job_description = len(job_description_list)
        matching_job_description = job_description_list.count(job_description_input)
        else_job_description = total_job_description - matching_job_description
        job_description_percentage = (matching_job_description / total_job_description) * 100 if total_job_description > 0 else 0

        gender_stats = db.execute(
            "SELECT gender, COUNT(*) as count FROM user WHERE job_description = ? GROUP BY gender", 
            (job_description_input,)
        ).fetchall()
        total_genders_for_job = sum(row['count'] for row in gender_stats)
        matching_genders_for_job = next((row['count'] for row in gender_stats if row['gender'] == gender_input), 0)
        else_genders_for_job = total_genders_for_job - matching_genders_for_job
        gender_percentage_for_job = (matching_genders_for_job / total_genders_for_job) * 100 if total_genders_for_job > 0 else 0

        flash("Scores updated successfully.")
        return render_template(
            "report.html",
            score1=score1, score2=score2, score3=score3, score4=score4, score5=score5, score6=score6,
            average_score1=average_scores[1], average_score2=average_scores[2], average_score3=average_scores[3],
            average_score4=average_scores[4], average_score5=average_scores[5], average_score6=average_scores[6],
            score6_rank_percentage=score6_rank_percentage, else_score6_rank_percentage=else_score6_rank_percentage,
            gender_input=gender_input, else_gender_input=else_gender_input, 
            matching_genders_for_job=matching_genders_for_job, else_genders_for_job=else_genders_for_job, 
            gender_percentage_for_job=gender_percentage_for_job,
            job_description_input=job_description_input, matching_job_description=matching_job_description, 
            else_job_description=else_job_description, job_description_percentage=job_description_percentage
        )

    except Exception as e:
        flash(str(e))
        return render_template("error.html")


    
@bp.route('/error')
def error():
    return render_template('error.html')

# bp
app.register_blueprint(bp)

# 資料庫連結
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)

