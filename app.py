from flask import Flask,render_template,jsonify,request
from database import load_jobs_from_db,load_job_from_db,add_application_to_db
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_admin, load_applications_from_db,add_admin_to_db
import os
from dotenv import load_dotenv
load_dotenv()


app=Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
@app.route('/')
def hello_world():
    jobs=load_jobs_from_db()
    return render_template('home.html', jobs=jobs,company_name='Aachar')

@app.route('/api/jobs')
def listing_jobs():
    jobs=load_jobs_from_db()
    return jsonify(jobs)

@app.route('/job/<id>')
def showing_job(id):
    job=load_job_from_db(id)
    if not job:
        return "Not Found",404
    return render_template('jobwebpage.html',job=job)

@app.route('/job/<id>/apply', methods=['POST'])
def job_apply(id):
    val=request.form #data is accessed using '.form'
    job=load_job_from_db(id)

    add_application_to_db(id,val)
    return render_template('application_submit.html',application=val,job=job)

# Add these routes
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if session.get('admin_logged_in'):
        return redirect('/admin/dashboard')

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Enhanced validation
        if not username or not password:
            error = 'Username and password are required'
        elif len(username) < 4:
            error = 'Username must be at least 4 characters'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters'
        elif password != confirm_password:
            error = 'Passwords do not match'
        else:
            existing_admin = get_admin(username)
            if existing_admin:
                error = 'Username already exists'
            else:
                hashed_pw = generate_password_hash(password)
                if add_admin_to_db(username, hashed_pw):
                    return redirect('/admin/login')
                else:
                    error = 'Registration failed - please try again later'

    return render_template('admin_signup.html', error=error)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect('/admin/dashboard')

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = get_admin(username)

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        error = 'Invalid credentials'

    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    applications = load_applications_from_db()
    return render_template('admin_dashboard.html', applications=applications)



if __name__=='__main__':
  app.run(host='0.0.0.0', debug=True)
  
