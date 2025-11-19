# app.py
import os
import csv
from io import StringIO
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, Response, jsonify
)
from flask_sqlalchemy import SQLAlchemy

# Login system
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

db = SQLAlchemy(app)

# ---------------- LOGIN MANAGER ---------------- #

login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------------- MODELS ---------------- #

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    grades = db.relationship("Grade", backref="student", cascade="all, delete-orphan")

    def average(self):
        if not self.grades:
            return None
        return round(sum(g.score for g in self.grades) / len(self.grades), 2)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)


# ---------------- FORMS ---------------- #

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Register")


# ---------------- LOGIN LOADER ---------------- #

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- ROUTES ---------------- #

@app.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "name")

    students_query = Student.query

    if q:
        like = f"%{q}%"
        students_query = students_query.filter(
            db.or_(Student.name.ilike(like), Student.roll_number.ilike(like))
        )

    students = students_query.all()

    # Sort by average
    if sort == "avg":
        students = sorted(
            students,
            key=lambda s: (s.average() is None, s.average() or 0),
            reverse=True,
        )
    else:
        students = sorted(students, key=lambda s: s.name.lower())

    return render_template("index.html", students=students)


@app.route("/student/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll = request.form.get("roll_number", "").strip()

        if not name or not roll:
            flash("Name and roll number required.", "danger")
            return redirect(url_for("add_student"))

        if Student.query.filter_by(roll_number=roll).first():
            flash("Roll number already exists.", "danger")
            return redirect(url_for("add_student"))

        db.session.add(Student(name=name, roll_number=roll))
        db.session.commit()

        flash("Student added.", "success")
        return redirect(url_for("index"))

    return render_template("add_student.html")


@app.route("/student/<int:student_id>")
@login_required
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("student_detail.html", student=student)


@app.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll = request.form.get("roll_number", "").strip()

        if not name or not roll:
            flash("Name and roll number required.", "danger")
            return redirect(url_for("edit_student", student_id=student.id))

        # Roll uniqueness check
        if roll != student.roll_number and Student.query.filter_by(roll_number=roll).first():
            flash("Roll number already taken.", "danger")
            return redirect(url_for("edit_student", student_id=student.id))

        student.name = name
        student.roll_number = roll
        db.session.commit()

        flash("Updated successfully.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    return render_template("edit_student.html", student=student)


@app.route("/student/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("index"))


@app.route("/student/<int:student_id>/grade/add", methods=["POST"])
@login_required
def add_grade(student_id):
    student = Student.query.get_or_404(student_id)

    subject = request.form.get("subject", "").strip()
    score = request.form.get("score", "").strip()

    if not subject or not score:
        flash("Subject and score required.", "danger")
        return redirect(url_for("student_detail", student_id=student.id))

    try:
        score_val = float(score)
    except ValueError:
        flash("Score must be numeric.", "danger")
        return redirect(url_for("student_detail", student_id=student.id))

    if not (0 <= score_val <= 100):
        flash("Score must be 0–100.", "danger")
        return redirect(url_for("student_detail", student_id=student.id))

    db.session.add(Grade(student_id=student.id, subject=subject, score=score_val))
    db.session.commit()

    flash("Grade added.", "success")
    return redirect(url_for("student_detail", student_id=student.id))


@app.route("/grade/<int:grade_id>/delete", methods=["POST"])
@login_required
def delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    sid = grade.student_id
    db.session.delete(grade)
    db.session.commit()
    flash("Grade deleted.", "success")
    return redirect(url_for("student_detail", student_id=sid))


# ---------------- CSV EXPORT ---------------- #

@app.route("/export/csv")
@login_required
def export_csv():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Name", "Roll", "Subject", "Score"])

    students = Student.query.order_by(Student.name).all()
    for s in students:
        if s.grades:
            for g in s.grades:
                writer.writerow([s.name, s.roll_number, g.subject, g.score])
        else:
            writer.writerow([s.name, s.roll_number, "", ""])

    output = si.getvalue()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )


# ---------------- CHART API ---------------- #

@app.route("/class-stats")
@login_required
def class_stats():
    students = Student.query.all()
    data = [
        {
            "name": s.name,
            "average": s.average() or 0
        }
        for s in students
    ]
    return jsonify(data)


# ---------------- AUTH ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data.strip()

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        user = User(username=username)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            print("Database created at", DB_PATH)

    app.run(debug=True)
