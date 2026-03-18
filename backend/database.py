import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root123',  # Change this to your MySQL password
        database='jobdb'
    )

def verify_user(user_id, user_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    table = "Student" if user_type == "student" else "Employer"
    id_col = "StudentID" if user_type == "student" else "EmployerID"
    cursor.execute(f"SELECT * FROM {table} WHERE {id_col} = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_personalized_feed(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT DISTINCT O.*, E.BusinessName FROM Opportunity O
        JOIN Posts P ON O.OppID = P.OppID
        JOIN Employer E ON P.EmployerID = E.EmployerID
        JOIN RequiredSkills RS ON O.OppID = RS.OppID
        JOIN Student S ON S.Zipcode = O.Zipcode
        WHERE S.StudentID = %s 
        AND RS.Skill IN (SELECT Skill FROM SkillTags WHERE StudentID = %s)
        AND O.Status = 'Active';
    """
    cursor.execute(sql, (student_id, student_id))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_all_active_jobs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT O.*, E.BusinessName FROM Opportunity O
        JOIN Posts P ON O.OppID = P.OppID
        JOIN Employer E ON P.EmployerID = E.EmployerID
        WHERE O.Status = 'Active' ORDER BY O.OppID DESC;
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_student_profile(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Student WHERE StudentID = %s", (student_id,))
    profile = cursor.fetchone()
    if profile:
        cursor.execute("SELECT Skill FROM SkillTags WHERE StudentID = %s", (student_id,))
        profile['Skills'] = [s['Skill'] for s in cursor.fetchall()] 
    cursor.close()
    conn.close()
    return profile

def add_student_skill(student_id, skill):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM SkillTags WHERE StudentID = %s AND Skill = %s", (student_id, skill))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO SkillTags (StudentID, Skill) VALUES (%s, %s)", (student_id, skill))
            conn.commit()
        success = True
    except:
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

def get_student_applications(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT O.RoleTitle, E.BusinessName, A.Status, A.ApplicationDate, O.OppID, A.ApplicationID, O.City
        FROM Job_application JA
        JOIN Application A ON JA.ApplicationID = A.ApplicationID
        JOIN Opportunity O ON JA.OppID = O.OppID
        JOIN Posts P ON O.OppID = P.OppID
        JOIN Employer E ON P.EmployerID = E.EmployerID
        WHERE JA.StudentID = %s ORDER BY A.ApplicationDate DESC;
    """
    cursor.execute(sql, (student_id,))
    apps = cursor.fetchall()
    cursor.close()
    conn.close()
    return apps

def get_student_app_details(app_id, opp_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT O.RoleTitle, O.Description, E.BusinessName, O.City 
        FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID JOIN Employer E ON P.EmployerID = E.EmployerID WHERE O.OppID = %s
    """, (opp_id,))
    job_info = cursor.fetchone()
    cursor.execute("SELECT Skill FROM RequiredSkills WHERE OppID = %s", (opp_id,))
    skills = [s['Skill'] for s in cursor.fetchall()]
    cursor.execute("SELECT Status FROM Application WHERE ApplicationID = %s", (app_id,))
    status = cursor.fetchone()['Status']
    cursor.close()
    conn.close()
    return {"job": job_info, "skills": skills, "status": status}

def get_employer_data(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT O.*, 
        (SELECT COUNT(*) FROM Job_application WHERE OppID = O.OppID) as AppCount 
        FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID WHERE P.EmployerID = %s;
    """
    cursor.execute(sql, (emp_id,))
    postings = cursor.fetchall()
    cursor.close()
    conn.close()
    return postings

def create_job_post(emp_id, title, desc, city, skills_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Opportunity (RoleTitle, Description, City, Status) VALUES (%s, %s, %s, 'Active')", (title, desc, city))
        opp_id = cursor.lastrowid
        cursor.execute("INSERT INTO Posts (EmployerID, OppID) VALUES (%s, %s)", (emp_id, opp_id))
        if skills_str:
            skills = [s.strip() for s in skills_str.split(',')]
            for s in skills:
                if s: cursor.execute("INSERT INTO RequiredSkills (OppID, Skill) VALUES (%s, %s)", (opp_id, s))
        conn.commit()
        success = True
    except:
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

def update_job_post(opp_id, role_title, description, city, req_students):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "UPDATE Opportunity SET RoleTitle=%s, Description=%s, City=%s, RequiredStudents=%s WHERE OppID=%s"
        cursor.execute(sql, (role_title, description, city, req_students, opp_id))
        conn.commit()
        success = True
    except:
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

def get_app_details(opp_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT A.Status, A.ApplicationID, S.FirstName, S.LastName,
        (SELECT AVG(ImpactScore) FROM PerformanceLedger WHERE ApplicationID = A.ApplicationID) as AvgImpact
        FROM Job_application JA
        JOIN Application A ON JA.ApplicationID = A.ApplicationID
        JOIN Student S ON JA.StudentID = S.StudentID
        WHERE JA.OppID = %s;
    """
    cursor.execute(sql, (opp_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_applicant_profile(app_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT S.*, A.Status, A.ApplicationID,
        (SELECT AVG(ImpactScore) FROM PerformanceLedger WHERE ApplicationID = A.ApplicationID) as AvgImpact
        FROM Job_application JA
        JOIN Application A ON JA.ApplicationID = A.ApplicationID
        JOIN Student S ON JA.StudentID = S.StudentID
        WHERE A.ApplicationID = %s
    """
    cursor.execute(sql, (app_id,))
    student = cursor.fetchone()
    if student:
        if student.get('ReliabilityScore'): student['ReliabilityScore'] = float(student['ReliabilityScore'])
        if student.get('AvgImpact'): student['AvgImpact'] = float(student['AvgImpact'])
        cursor.execute("SELECT Skill FROM SkillTags WHERE StudentID = %s", (student['StudentID'],))
        student['Skills'] = [s['Skill'] for s in cursor.fetchall()]
    cursor.close()
    conn.close()
    return student

def accept_application(app_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE Application SET Status = 'Accepted' WHERE ApplicationID = %s", (app_id,))
        cursor.execute("SELECT OppID FROM Job_application WHERE ApplicationID = %s", (app_id,))
        row = cursor.fetchone()
        
        if row:
            opp_id = row['OppID']
            cursor.execute("""
                SELECT O.RequiredStudents, 
                       (SELECT COUNT(*) FROM Job_application JA 
                        JOIN Application A ON JA.ApplicationID = A.ApplicationID 
                        WHERE JA.OppID = O.OppID AND A.Status = 'Accepted') as AcceptedCount
                FROM Opportunity O WHERE O.OppID = %s
            """, (opp_id,))
            quota = cursor.fetchone()
            
            if quota and quota['AcceptedCount'] >= quota['RequiredStudents']:
                cursor.execute("UPDATE Opportunity SET Status = 'Assigned' WHERE OppID = %s", (opp_id,))
                cursor.execute("""
                    UPDATE Application A
                    JOIN Job_application JA ON A.ApplicationID = JA.ApplicationID
                    SET A.Status = 'Rejected'
                    WHERE JA.OppID = %s AND A.Status = 'Pending'
                """, (opp_id,))
        conn.commit()
        success = True
    except Exception as e:
        print(f"Accept Error: {e}")
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

def apply_for_job(student_id, opp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Job_application WHERE StudentID = %s AND OppID = %s", (student_id, opp_id))
        if cursor.fetchone():
            return False, "You have already applied for this role."
        
        cursor.execute("INSERT INTO Application (ApplicationDate, Status) VALUES (CURDATE(), 'Pending')")
        app_id = cursor.lastrowid
        cursor.execute("INSERT INTO Job_application (ApplicationID, OppID, StudentID) VALUES (%s, %s, %s)", (app_id, opp_id, student_id))
        conn.commit()
        success, msg = True, "Application Submitted Successfully!"
    except Exception as e:
        print(f"Apply Error: {e}")
        success, msg = False, "Database Error. Please try again."
    finally:
        cursor.close()
        conn.close()
    return success, msg

def get_job_details(opp_id, student_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT O.*, E.BusinessName, E.VerifiedIdentity, E.TrustScore
        FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID
        JOIN Employer E ON P.EmployerID = E.EmployerID WHERE O.OppID = %s
    """
    cursor.execute(sql, (opp_id,))
    job = cursor.fetchone()
    if job:
        for key, value in job.items():
            if hasattr(value, '__float__'): job[key] = float(value)
        cursor.execute("SELECT Skill FROM RequiredSkills WHERE OppID = %s", (opp_id,))
        job['Skills'] = [s['Skill'] for s in cursor.fetchall()]
        
        job['HasApplied'] = False
        if student_id:
            cursor.execute("SELECT 1 FROM Job_application WHERE OppID = %s AND StudentID = %s", (opp_id, student_id))
            if cursor.fetchone():
                job['HasApplied'] = True
    cursor.close()
    conn.close()
    return job

def search_opportunities(query):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    term = f"%{query}%"
    sql = """
        SELECT DISTINCT O.* FROM Opportunity O
        LEFT JOIN RequiredSkills RS ON O.OppID = RS.OppID
        WHERE O.Status = 'Active' 
        AND (O.RoleTitle LIKE %s OR RS.Skill LIKE %s OR O.City LIKE %s);
    """
    cursor.execute(sql, (term, term, term))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results