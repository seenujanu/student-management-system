from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3, io, csv

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secret-key"
DB_NAME = "students.db"

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT,
        class TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    )""")
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    q = request.args.get("q", "")
    conn = get_db()
    if q:
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll LIKE ? OR class LIKE ?",
            (f"%{q}%", f"%{q}%", f"%{q}%")
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", students=students, q=q)

@app.route("/add", methods=["GET","POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        sclass = request.form["class"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn = get_db()
        conn.execute("INSERT INTO students (name,roll,class,phone,email,address) VALUES (?,?,?,?,?,?)",
            (name, roll, sclass, phone, email, address))
        conn.commit()
        conn.close()
        flash("Student added successfully.","success")
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_student(id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?",(id,)).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        sclass = request.form["class"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]
        conn.execute("""UPDATE students SET name=?, roll=?, class=?, phone=?, email=?, address=? WHERE id=?""",
            (name,roll,sclass,phone,email,address,id))
        conn.commit()
        conn.close()
        flash("Student updated.","success")
        return redirect(url_for("index"))
    conn.close()
    return render_template("edit.html", student=student)

@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?",(id,))
    conn.commit()
    conn.close()
    flash("Student deleted.","info")
    return redirect(url_for("index"))

@app.route("/export")
def export_csv():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Name","Roll","Class","Phone","Email","Address"])
    for r in rows:
        writer.writerow([r["id"],r["name"],r["roll"],r["class"],r["phone"],r["email"],r["address"]])
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                     as_attachment=True, download_name="students.csv")

if __name__=="__main__":
    init_db()
    app.run(debug=True)
