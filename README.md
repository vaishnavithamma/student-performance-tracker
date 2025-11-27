🎓 Student Performance Tracker

A Python and Flask-based web application designed to help teachers track student performance across multiple subjects.
The system allows adding students, assigning grades, viewing reports, calculating averages, and storing data persistently using a database.

🚀 Features

➕ Add Students (Name & Roll Number)

✏️ Add Grades for subjects (Math, Science, English, etc.)

📄 View Student Details

📊 Calculate Average Grades

🧠 Validations:

Roll number uniqueness

Grade range checks (0–100)

💾 Database-powered storage (SQLite)

🌐 Web-based interface using Flask

☁️ Deployable on Heroku / Render / PythonAnywhere

🗂️ Project Structure
student-performance-tracker/
│── app.py
│── init_db.py
│── requirements.txt
│── Procfile
│── students.db (optional; generated automatically)
│── static/
│── templates/
└── README.md

⚙️ Installation & Running Locally
1️⃣ Clone the Repository
git clone https://github.com/vaishnavithamma/student-performance-tracker
cd student-performance-tracker

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Initialize the Database (Only first time)
python init_db.py

4️⃣ Run the Application
python app.py

5️⃣ Open in Browser
http://127.0.0.1:5000/

🧑‍🏫 How to Use the Application
➤ 1. Add a Student

Go to Add Student page

Enter name + roll number

Submit

✔ The student will be stored in the database.

➤ 2. Add Grades

Select a student by roll number

Assign subject-wise grades between 0 and 100

Submit

✔ The grades are saved and linked to that student.

➤ 3. View Student Details

Choose a student

View:

Name

Roll Number

All subject grades

Calculated average score

➤ 4. Reports

Average grade calculation is performed automatically.

Some deployments may also include:

Topper per subject

Class average (optional bonus)

🌍 Deployment

This project includes:

requirements.txt

Procfile

These files make it ready for deployment on:

Heroku

Render

PythonAnywhere

Railway

Once deployed, the application link should be provided below.

🔗 Live Application

👉 Deployed Link: Coming Soon
(Replace this once deployed.)

🧾 Deliverables Included

✔ Python scripts & Flask app
✔ requirements.txt
✔ Procfile
✔ This README user guide
✔ Deployment link (after hosting)

🙌 Credits

Developed as part of an internship task to demonstrate:

Python fundamentals

Object-Oriented Programming

Database integration

Flask web development

Deployment workflow

📜 License

This project is for educational purposes and can be extended or improved.
