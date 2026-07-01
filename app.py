from flask import Flask, request, render_template_string, session, redirect
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.urandom(16)
DB = "/tmp/web1_users.db"
FLAG = "Flag_CT8{sq1_1nj3ct10n_byp@ss_l0g1n_2026}"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("INSERT INTO users VALUES (1,'admin','s3cr3tP@ss!xZ9','admin')")
    c.execute("INSERT INTO users VALUES (2,'guest','guest123','user')")
    c.execute("INSERT INTO users VALUES (3,'alice','al1c3p@ss','user')")
    conn.commit()
    conn.close()

LOGIN = """
<!doctype html>
<html>
<head>
  <title>CyberTec8 Staff Portal</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #0f1117; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    .container { max-width: 420px; margin: 100px auto; padding: 40px; background: #1a1d27; border-radius: 12px; border: 1px solid #2d3748; }
    h2 { color: #63b3ed; margin-bottom: 6px; }
    .subtitle { color: #718096; font-size: 0.85em; margin-bottom: 28px; }
    label { display: block; font-size: 0.85em; color: #a0aec0; margin-bottom: 6px; margin-top: 16px; }
    input { width: 100%; padding: 10px 14px; background: #2d3748; border: 1px solid #4a5568; border-radius: 8px; color: #e2e8f0; font-size: 0.95em; }
    input:focus { outline: none; border-color: #63b3ed; }
    button { width: 100%; margin-top: 24px; padding: 11px; background: #2b6cb0; border: none; border-radius: 8px; color: white; font-size: 1em; cursor: pointer; }
    button:hover { background: #2c5282; }
    .error { margin-top: 16px; padding: 10px 14px; background: #742a2a; border-radius: 8px; color: #feb2b2; font-size: 0.9em; }
    .hint { margin-top: 20px; font-size: 0.78em; color: #4a5568; text-align: center; }
  </style>
</head>
<body>
  <div class="container">
    <h2>🔒 Staff Portal</h2>
    <p class="subtitle">CyberTec8 Internal System</p>
    <form method="post">
      <label>Username</label>
      <input name="username" placeholder="Enter username" autocomplete="off">
      <label>Password</label>
      <input name="password" type="password" placeholder="Enter password">
      <button type="submit">Login</button>
    </form>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <p class="hint">Authorized personnel only</p>
  </div>
</body>
</html>
"""

DASHBOARD = """
<!doctype html>
<html>
<head>
  <title>Dashboard</title>
  <style>
    body { background: #0f1117; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    .container { max-width: 600px; margin: 80px auto; padding: 40px; background: #1a1d27; border-radius: 12px; border: 1px solid #2d3748; }
    h2 { color: #68d391; margin-bottom: 20px; }
    .flag-box { background: #1c4532; border: 1px solid #276749; border-radius: 8px; padding: 16px 20px; font-family: monospace; font-size: 1.1em; color: #9ae6b4; margin: 20px 0; word-break: break-all; }
    .user-box { background: #2d3748; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 0.9em; color: #a0aec0; }
    a { color: #63b3ed; }
  </style>
</head>
<body>
  <div class="container">
    <h2>✅ Welcome, {{ user }}!</h2>
    <div class="user-box">Role: <b>{{ role }}</b></div>
    {% if is_admin %}
    <p>Admin panel unlocked. Here is your flag:</p>
    <div class="flag-box">{{ flag }}</div>
    {% else %}
    <p>You are logged in as a regular user. Only <b>admin</b> can see the flag.</p>
    {% endif %}
    <a href="/logout">← Logout</a>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # VULNERABLE: raw string interpolation
        query = f"SELECT * FROM users WHERE username='{u}' AND password='{p}'"
        try:
            c.execute(query)
            row = c.fetchone()
        except sqlite3.Error:
            row = None
            error = "SQL Error — check your syntax."
        conn.close()
        if row:
            session["user"] = row[1]
            session["role"] = row[3]
            return redirect("/dashboard")
        error = error or "Invalid username or password."
    return render_template_string(LOGIN, error=error)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template_string(
        DASHBOARD,
        user=session["user"],
        role=session["role"],
        is_admin=(session["role"] == "admin"),
        flag=FLAG
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=7001, debug=False)
