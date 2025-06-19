from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv
from io import StringIO

from models import db, User, Candidate, Vote

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

db.init_app(app)

# ----------------------------- HOME -----------------------------
@app.route('/')
def home():
    return render_template('index.html')


# ----------------------------- REGISTER -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        file = request.files.get('voter_id')

        if not username or not password:
            flash('Username and password are required.', 'warning')
            return render_template('register.html')

        if not file:
            flash('Voter ID file is required.', 'warning')
            return render_template('register.html')

        filename = secure_filename(file.filename)
        if filename == '':
            flash('Invalid file name.', 'danger')
            return render_template('register.html')

        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            upload_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            new_user = User(username=username, password=password, voter_id_path=file_path)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('File type not allowed. Please upload PDF, PNG, JPG, or JPEG.', 'danger')

    return render_template('register.html')


# ----------------------------- LOGIN -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash(f"Welcome {username}!", "success")
            return redirect(url_for('dashboard' if user.is_admin else 'vote'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')


# ----------------------------- LOGOUT -----------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


# ----------------------------- USER VOTING -----------------------------
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session or session.get('is_admin'):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.has_voted:
        flash('You have already voted.', 'warning')
        return redirect(url_for('results'))

    candidates = Candidate.query.all()

    if request.method == 'POST':
        candidate_id = request.form.get('candidate')
        if not candidate_id:
            flash('Please select a candidate.', 'warning')
        else:
            vote = Vote(user_id=user.id, candidate_id=int(candidate_id))
            user.has_voted = True
            db.session.add(vote)
            db.session.commit()
            flash('Your vote has been submitted!', 'success')
            return redirect(url_for('results'))

    return render_template('vote.html', candidates=candidates)


# ----------------------------- RESULTS -----------------------------
@app.route('/results')
def results():
    candidates = Candidate.query.all()
    vote_counts = {candidate.id: 0 for candidate in candidates}
    all_votes = Vote.query.all()

    for vote in all_votes:
        vote_counts[vote.candidate_id] += 1

    results = [{
        'candidate': Candidate.query.get(cid),
        'votes': vote_counts[cid]
    } for cid in vote_counts]

    return render_template('results.html', results=results)


# ----------------------------- ADMIN DASHBOARD -----------------------------
@app.route('/add_candidate', methods=['GET', 'POST'])
def add_candidate():
    if not session.get('is_admin'):
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        party = request.form['party'].strip()
        image = request.files.get('image')

        image_path = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                folder = os.path.join(app.config['UPLOAD_FOLDER'], 'candidates')
                os.makedirs(folder, exist_ok=True)
                full_path = os.path.join(folder, filename)
                image.save(full_path)
                image_path = os.path.join('uploads', 'candidates', filename)  # Path for static display
            else:
                flash('Invalid image format.', 'danger')
                return redirect(url_for('dashboard'))

        if name and party:
            candidate = Candidate(name=name, party=party, image_path=image_path)
            db.session.add(candidate)
            db.session.commit()
            flash('Candidate added successfully!', 'success')
        else:
            flash('All fields are required.', 'warning')

    return redirect(url_for('dashboard'))



# ----------------------------- EXPORT TO CSV -----------------------------
@app.route('/export_votes')
def export_votes():
    if not session.get('is_admin'):
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['User ID', 'Candidate ID'])

    votes = Vote.query.all()
    for vote in votes:
        writer.writerow([vote.user_id, vote.candidate_id])

    output.seek(0)
    return send_file(
        StringIO(output.read()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='votes_export.csv'
    )


# ----------------------------- MAIN -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
