from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from datetime import datetime, timedelta
import random, string, os, pymysql, re, requests

# Flask + DB setup
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:cana8rias@localhost/errs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

slack_channels = {
    'recognition': 'https://hooks.slack.com/services/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',
    'new_member': 'https://hooks.slack.com/services/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',
    'rewards': 'https://hooks.slack.com/services/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',
    'feedback': 'https://hooks.slack.com/services/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'
}



def send_to_slack(channel, message):
    url = slack_channels.get(channel)
    if url:
        try:
            requests.post(url, json={'text': message})
        except Exception as e:
            print("Slack Error:", e)

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)  # ✅ Add this line


class Person(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    receiver = db.Column(db.String(100))
    sender_department = db.Column(db.String(100))
    receiver_department = db.Column(db.String(100))
    message = db.Column(db.Text)
    badge = db.Column(db.String(50))
    employee_id = db.Column(db.String(10))
    timestamp = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.Text)
    timestamp = db.Column(db.String(100))

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(100))
    reward = db.Column(db.String(100))
    reason = db.Column(db.Text)
    timestamp = db.Column(db.String(100))

# Routes
@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        flash("⚠️ You need an account to access that page.")
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_manager'] = user.is_manager  # Make sure this is set
            session['logged_in'] = True

            return redirect(url_for('home'))

        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_manager = True if 'is_manager' in request.form else False  # ✅

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists")

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, is_manager=is_manager)
        db.session.add(new_user)
        db.session.commit()

        send_to_slack('new_member', f"👋 New user *{username}* just registered an account on TC Corp.")
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/submit_recognition', methods=['GET', 'POST'])
def submit_recognition():
    if 'user_id' not in session:
        flash("⚠️ You need an account to access that page.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # ... [collect form fields as usual]
        sender = request.form['sender']
        receiver = request.form['receiver']
        badge = request.form['badge']
        message = request.form['message']
        sender_dept = request.form['sender_department']
        receiver_dept = request.form['receiver_department']

        if not re.match("^[A-Za-z ]+$", sender) or not re.match("^[A-Za-z ]+$", receiver):
            return render_template('submit_recognition.html', error="Names must only contain letters and spaces.")

        # Person + Recognition creation
        email = f"{receiver.replace(' ', '').lower()}@TCCorp.org"
        emp_id = generate_id()

        if not Person.query.filter_by(username=receiver).first():
            db.session.add(Person(id=emp_id, username=receiver, email=email, department=receiver_dept))
            db.session.commit()

        new_rec = Recognition(
            sender=sender, receiver=receiver, sender_department=sender_dept,
            receiver_department=receiver_dept, message=message, badge=badge,
            employee_id=emp_id, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            approved=False
        )
        db.session.add(new_rec)
        db.session.commit()

        # ✅ Render the same page with success popup
        return render_template('submit_recognition.html', success="Recognition submitted and is pending manager approval.")

    return render_template('submit_recognition.html')



@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        flash("⚠️ You need an account to access that page.")
        return redirect(url_for('login'))

    recs = Recognition.query.filter_by(approved=True).all()
    score = {}
    for r in recs:
        score[r.receiver] = score.get(r.receiver, 0) + 1
    sorted_scores = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return render_template('leaderboard.html', leaderboard=sorted_scores, recognitions=recs)


@app.route('/feedback_form', methods=['GET', 'POST'])
def feedback_form():
    if 'user_id' not in session:
        flash("⚠️ You need an account to access that page.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        fb = Feedback(feedback=request.form['feedback'], timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(fb)
        db.session.commit()
        send_to_slack('feedback', f"📝 New Feedback: \"{fb.feedback}\"")
        return redirect(url_for('home'))
    return render_template('feedback_form.html')

@app.route('/report')
def report():
    if 'user_id' not in session:
        flash("⚠️ You need an account to access that page.")
        return redirect(url_for('login'))

    recs = Recognition.query.filter_by(approved=True).all()
    return render_template('report.html', recognitions=recs)


@app.route('/submit_reward', methods=['GET', 'POST'])
def submit_reward():
    if 'user_id' not in session:
        flash("⚠️ You need an account to access that page.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        r = Reward(
            recipient=request.form['recipient'],
            reward=request.form['reward'],
            reason=request.form['reason'],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(r)
        db.session.commit()
        send_to_slack('rewards', f"🏆 {r.recipient} has earned: *{r.reward}*\nReason: {r.reason}")
        return redirect(url_for('home'))

    thirty_days_ago = datetime.now() - timedelta(days=30)
    recents = db.session.execute(text("SELECT * FROM recognition WHERE STR_TO_DATE(timestamp, '%Y-%m-%d %H:%i:%s') >= :date"), {"date": thirty_days_ago.strftime('%Y-%m-%d %H:%M:%S')}).fetchall()
    counts = {}
    for r in recents:
        counts[r.receiver] = counts.get(r.receiver, 0) + 1
    eligible = [name for name, count in counts.items() if count >= 3]
    return render_template('submit_reward.html', eligible=eligible)

@app.route('/manager')
def manager_view():
    if not session.get('is_manager'):
        flash("Unauthorized access.")
        return redirect(url_for('home'))
    pending = Recognition.query.filter_by(approved=False).all()
    return render_template('manager_pending.html', pending=pending)


@app.route('/manager/approve/<int:rec_id>', methods=['POST'])
def approve_recognition(rec_id):
    rec = Recognition.query.get(rec_id)
    if rec:
        rec.approved = True
        db.session.commit()
        send_to_slack('recognition', f"🎉 *New Recognition!*\nFrom: {rec.sender} → To: {rec.receiver}\n🏅 Badge: {rec.badge}\n📝 Message: {rec.message}")
    return redirect(url_for('manager_view'))

@app.route('/manager/deny/<int:rec_id>', methods=['POST'])
def deny_recognition(rec_id):
    rec = Recognition.query.get(rec_id)
    if rec:
        db.session.delete(rec)
        db.session.commit()
    return redirect(url_for('manager_view'))

@app.route('/manager/clear_all', methods=['POST'])
def clear_recognitions():
    Recognition.query.delete()
    db.session.commit()
    flash(" All recognitions have been cleared.")
    return redirect(request.referrer or url_for('manager_view'))


# ---------- RUN ----------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)