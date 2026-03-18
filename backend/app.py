from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))
app.secret_key = 'super_secret_resume_key' 

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = None

    if request.method == 'POST':
        user_id = (request.form.get('user_id') or request.form.get('id', '')).strip()
        user_type = (request.form.get('user_type') or request.form.get('type', '')).lower()

        user = database.verify_user(user_id, user_type)

        if user:
            session['user_id'] = user_id
            session['user_type'] = user_type
            return redirect(url_for('account'))
        else:
            error_msg = "Invalid ID for this account type."

    return render_template('login.html', error=error_msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user_id' not in session: return redirect(url_for('login'))
    jobs, all_jobs = [], []
    if session['user_type'] == 'student':
        jobs = database.get_personalized_feed(session['user_id'])
        all_jobs = database.get_all_active_jobs()
    return render_template('home.html', jobs=jobs, all_jobs=all_jobs, user_type=session['user_type'])

@app.route('/search')
def search():
    if 'user_id' not in session: return redirect(url_for('login'))
    query = request.args.get('q', '')
    results = database.search_opportunities(query) if query else []
    return render_template('search.html', results=results, query=query)

@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_type = session.get('user_type')
    user_id = session['user_id']
    
    if user_type == 'employer':
        posts = database.get_employer_data(user_id)
        return render_template('account.html', posts=posts, user_type=user_type)
    else:
        apps = database.get_student_applications(user_id)
        profile = database.get_student_profile(user_id)
        return render_template('account.html', apps=apps, profile=profile, user_type=user_type)

# --- APIs ---
@app.route('/api/job/<opp_id>')
def api_job_details(opp_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    student_id = session['user_id'] if session['user_type'] == 'student' else None
    job = database.get_job_details(opp_id, student_id)
    return jsonify(job) if job else (jsonify({"error": "Not found"}), 404)

@app.route('/api/details/<opp_id>')
def api_details(opp_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(database.get_app_details(opp_id))

@app.route('/api/student_app/<app_id>/<opp_id>')
def api_student_app_details(app_id, opp_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(database.get_student_app_details(app_id, opp_id))

@app.route('/api/applicant_details/<app_id>')
def api_applicant_details(app_id):
    if 'user_id' not in session or session['user_type'] != 'employer': return jsonify({"error": "Unauthorized"}), 401
    return jsonify(database.get_applicant_profile(app_id))

@app.route('/api/accept_app/<app_id>', methods=['POST'])
def api_accept_app(app_id):
    if 'user_id' not in session or session['user_type'] != 'employer': return jsonify({"success": False}), 401
    success = database.accept_application(app_id)
    return jsonify({"success": success})

@app.route('/api/apply/<opp_id>', methods=['POST'])
def api_apply(opp_id):
    if 'user_id' not in session or session['user_type'] != 'student': 
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    success, message = database.apply_for_job(session['user_id'], opp_id)
    return jsonify({"success": success, "message": message})

@app.route('/api/add_skill', methods=['POST'])
def api_add_skill():
    if 'user_id' not in session or session['user_type'] != 'student': return jsonify({"success": False}), 401
    data = request.json
    success = database.add_student_skill(session['user_id'], data.get('skill'))
    return jsonify({"success": success})

@app.route('/api/create_job', methods=['POST'])
def api_create_job():
    if 'user_id' not in session or session['user_type'] != 'employer': return jsonify({"success": False}), 401
    data = request.json
    success = database.create_job_post(session['user_id'], data['Title'], data['Description'], data['Location'], data['Skills'])
    return jsonify({"success": success})

@app.route('/api/edit_job/<opp_id>', methods=['POST'])
def api_edit_job(opp_id):
    if 'user_id' not in session or session['user_type'] != 'employer': return jsonify({"success": False}), 401
    data = request.json
    success = database.update_job_post(opp_id, data['RoleTitle'], data['Description'], data['City'], data['RequiredStudents'])
    return jsonify({"success": success})

if __name__ == '__main__':
    app.run(debug=True)