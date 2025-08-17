# -------------------------
# Imports
# -------------------------
from flask import Flask, render_template, url_for, request, redirect, session 
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
import csv
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import os

# -------------------------
# Flask App Configuration
# -------------------------
app = Flask(__name__)

# -------------------------
# OpenAI Configuration
# -------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# -------------------------
# SQLAlchemy Configuration
# -------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("MYSQL_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------
# Database Models
# -------------------------
class User(db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # stored as hashed value

class Question(db.Model):
    """Question bank for coding interview practice"""
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)

# -------------------------
# Middleware: Prevent cached pages after logout
# -------------------------
@app.after_request
def add_no_cache_headers(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# -------------------------
# Routes
# -------------------------

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["email"] = user.email
            return render_template("logged_in.html", user=user)
        elif user and not check_password_hash(user.password, password):
            return render_template("login.html", error="Incorrect Email or Password")
        else:
            return render_template("login.html", error="Email does not Exist")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name  = request.form.get("last_name")
        email      = request.form.get("email")
        password   = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            return render_template("signup.html", error="Email Already Exists")

        hashed_password = generate_password_hash(password)
        new_user = User(first_name=first_name, last_name=last_name,
                        email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"]    = new_user.id
        session["first_name"] = new_user.first_name

        return render_template("logged_in.html", user=new_user)

    return render_template("signup.html")

@app.route("/logged_in", methods=["GET", "POST"])
def logged_in():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("logged_in.html")

@app.route("/generate_question", methods=["GET", "POST"])
def generate_question():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        company   = request.form.get("company")
        topic     = request.form.get("topic")
        difficulty= request.form.get("difficulty")

        random_question = (Question.query
                           .filter_by(topic=topic, company=company, difficulty=difficulty)
                           .order_by(func.rand())
                           .first())

        ai_prompt = f"""
            You are given a coding interview question: '{random_question.question}'. 
            Reformat it into the following strict format: bassicaly have one line space after every thing, 
            dont write the [problem] or anything Remeber you do not need to add these [Problem] or [fucntion] 
            i just gave them as examples do not include these in the question please 
            
            [Problem] two sentences describing the task propely leetcode style, like it should be clear [Function]
            Write "param:" followed by the function name and parameter(s). 
            [Examples] Write exactly two examples in this style: 
            Input: <example input> Output: <example output> 
            
            Rules: - Do NOT add explanations, headings, or extra text. - Do NOT write code. - 
            Keep wording minimal and consistent. - Always give exactly two examples.
        """

        question_text = ai_call(ai_prompt)
        return render_template("logged_in.html", question_text=question_text)

    return render_template("logged_in.html")

@app.route("/generate_solution", methods=["GET", "POST"])
def generate_solution():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        solution_code = request.form.get("code")      
        hello         = request.form.get("question_hello")  

        solution_prompt = f"""
        You are validating a coding interview solution. Question: {hello} 
        User's Code: {solution_code} 
        Instructions: - If the solution is fully correct, reply with only: "Correct ✅" 
        If it's wrong: 
        1. Briefly explain why it's incorrect in 1–2 lines. 
        2. Provide the corrected solution in the same language as the user’s code. 
        3. Keep your response concise. Do not include headings, markdown, or extra explanations.
        """

        solution = ai_call(solution_prompt)
        return render_template("logged_in.html", solution=solution)

    return render_template("logged_in.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")

# -------------------------
# Helper Functions
# -------------------------
def ai_call(ai_prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate summary: {e}"

# -------------------------
# Database Setup Utilities
# -------------------------
with app.app_context():
    db.create_all()

def csv_to_db():
    with open("top_tier_600_questions.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            company, difficulty, topic, question = row
            new_question = Question(company=company, difficulty=difficulty,
                                    topic=topic, question=question)
            db.session.add(new_question)
            db.session.commit()

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
