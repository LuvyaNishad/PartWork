import mysql.connector
import hashlib
import time

def get_db_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='root123', database='jobdb'
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PaymentMethods (
            UserID VARCHAR(50), UserType VARCHAR(20), Token VARCHAR(100), PRIMARY KEY(UserID, UserType)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def save_payment_token(user_id, user_type, token):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO PaymentMethods (UserID, UserType, Token) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Token = %s", (user_id, user_type, token, token))
        conn.commit()
        return True
    except: return False
    finally:
        cursor.close()
        conn.close()

def get_payment_token(user_id, user_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Token FROM PaymentMethods WHERE UserID = %s AND UserType = %s", (user_id, user_type))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row['Token'] if row else None

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
        SELECT DISTINCT O.*, E.BusinessName FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID
        JOIN Employer E ON P.EmployerID = E.EmployerID JOIN RequiredSkills RS ON O.OppID = RS.OppID JOIN Student S ON S.Zipcode = O.Zipcode
        WHERE S.StudentID = %s AND RS.Skill IN (SELECT Skill FROM SkillTags WHERE StudentID = %s) AND O.Status = 'Active';
    """
    cursor.execute(sql, (student_id, student_id))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_all_active_jobs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT O.*, E.BusinessName FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID JOIN Employer E ON P.EmployerID = E.EmployerID WHERE O.Status = 'Active' ORDER BY O.OppID DESC")
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
        if profile.get('ReliabilityScore'): profile['ReliabilityScore'] = float(profile['ReliabilityScore'])
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
    except: success = False
    finally:
        cursor.close()
        conn.close()
    return success

def get_student_applications(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT O.RoleTitle, E.BusinessName, A.Status, A.ApplicationDate, O.OppID, A.ApplicationID, O.City, O.Status as JobStatus
        FROM Job_application JA JOIN Application A ON JA.ApplicationID = A.ApplicationID JOIN Opportunity O ON JA.OppID = O.OppID
        JOIN Posts P ON O.OppID = P.OppID JOIN Employer E ON P.EmployerID = E.EmployerID WHERE JA.StudentID = %s ORDER BY A.ApplicationDate DESC;
    """
    cursor.execute(sql, (student_id,))
    apps = cursor.fetchall()
    cursor.close()
    conn.close()
    return apps

def get_student_app_details(app_id, opp_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT O.RoleTitle, O.Description, E.BusinessName, O.City, O.Status as JobStatus FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID JOIN Employer E ON P.EmployerID = E.EmployerID WHERE O.OppID = %s", (opp_id,))
    job_info = cursor.fetchone()
    
    cursor.execute("SELECT Skill FROM RequiredSkills WHERE OppID = %s", (opp_id,))
    skills = [s['Skill'] for s in cursor.fetchall()]
    
    cursor.execute("SELECT Status FROM Application WHERE ApplicationID = %s", (app_id,))
    status = cursor.fetchone()['Status']

    cursor.execute("SELECT MilestoneID, Description, Payout, Deadline, ApprovalStatus FROM MilestoneLedger WHERE OppID = %s", (opp_id,))
    milestones = cursor.fetchall()

    cursor.execute("SELECT TotalAmount FROM ProjWallet WHERE OppID = %s", (opp_id,))
    wallet = cursor.fetchone()
    total_escrow = float(wallet['TotalAmount']) if wallet else 0.0

    cursor.execute("SELECT SUM(Payout) as ApprovedTotal FROM MilestoneLedger WHERE OppID = %s AND ApprovalStatus = 'Approved'", (opp_id,))
    approved = cursor.fetchone()['ApprovedTotal'] or 0.0

    cursor.execute("SELECT ReviewerRole, MetricType, ImpactScore FROM PerformanceLedger WHERE ApplicationID = %s", (app_id,))
    feedback = cursor.fetchall()

    cursor.execute("SELECT ScheduledTime FROM Interview WHERE ApplicationID = %s", (app_id,))
    interview = cursor.fetchone()
    interview_time = str(interview['ScheduledTime']) if interview and interview['ScheduledTime'] else None

    cursor.close()
    conn.close()
    return {"job": job_info, "skills": skills, "status": status, "milestones": milestones, "escrow": total_escrow - float(approved), "feedback": feedback, "interviewTime": interview_time}

def get_employer_data(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT O.*, (SELECT COUNT(*) FROM Job_application WHERE OppID = O.OppID) as AppCount 
        FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID WHERE P.EmployerID = %s;
    """
    cursor.execute(sql, (emp_id,))
    postings = cursor.fetchall()
    cursor.close()
    conn.close()
    
    conn2 = get_db_connection()
    c2 = conn2.cursor(dictionary=True)
    c2.execute("SELECT TrustScore FROM Employer WHERE EmployerID = %s", (emp_id,))
    ts = c2.fetchone()
    c2.close()
    conn2.close()
    return postings, (float(ts['TrustScore']) if ts and ts['TrustScore'] else 5.0)

def schedule_interview(app_id, interview_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fix the HTML5 datetime-local format 'YYYY-MM-DDThh:mm' to MySQL format 'YYYY-MM-DD hh:mm:00'
        formatted_time = interview_time.replace('T', ' ')
        if len(formatted_time) == 16:  # If seconds are missing, add them
            formatted_time += ':00'

        cursor.execute("""
            INSERT INTO Interview (ApplicationID, ScheduledTime, MeetingType, ApplicationStatus) 
            VALUES (%s, %s, 'Zoom', 'Scheduled')
            ON DUPLICATE KEY UPDATE ScheduledTime = VALUES(ScheduledTime), ApplicationStatus = 'Scheduled'
        """, (app_id, formatted_time))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error scheduling interview: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def check_both_rated(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Count how many reviews exist for this specific application
        cursor.execute("SELECT COUNT(*) FROM PerformanceLedger WHERE ApplicationID = %s", (app_id,))
        count = cursor.fetchone()[0]
        
        # If count is 2 (or more), both parties have reviewed!
        return count >= 2
    except Exception as e:
        print(f"Check rating error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def withdraw_application(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Application SET Status = 'Withdrawn' WHERE ApplicationID = %s", (app_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Withdraw Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_job_post(employer_id, title, description, location, skills_str, funds, milestones, interview_required=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Create the Opportunity (Now includes interview_required)
        cursor.execute("""
            INSERT INTO Opportunity (RoleTitle, Description, City, RequiredStudents, Status, Type, InterviewRequired)
            VALUES (%s, %s, %s, 1, 'Active', 'Freelance', %s)
        """, (title, description, location, interview_required))
        
        opp_id = cursor.lastrowid

        # 2. Link to Employer via Posts table
        cursor.execute("INSERT INTO Posts (EmployerID, OppID) VALUES (%s, %s)", (employer_id, opp_id))

        # 3. Add Required Skills
        if skills_str:
            skills = [s.strip() for s in skills_str.split(',')]
            for s in skills:
                if s: 
                    cursor.execute("INSERT INTO RequiredSkills (OppID, Skill) VALUES (%s, %s)", (opp_id, s))

        # 4. Add Milestones
        for m in milestones:
            cursor.execute("""
                INSERT INTO MilestoneLedger (OppID, Description, Payout, Deadline, ApprovalStatus)
                VALUES (%s, %s, %s, %s, 'Pending')
            """, (opp_id, m['desc'], m['payout'], m['deadline']))

        # 5. Create Wallet
        cursor.execute("INSERT INTO ProjWallet (OppID, TotalAmount, Status) VALUES (%s, %s, 'Funded')", (opp_id, funds))
        
        conn.commit()
        return True, "Job Created Successfully!"
    except Exception as e:
        print(f"Error creating job: {e}")
        return False, "Database error while creating job."
    finally:
        cursor.close()
        conn.close()

def update_job_post(opp_id, role_title, description, city, req_students):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Opportunity SET RoleTitle=%s, Description=%s, City=%s, RequiredStudents=%s WHERE OppID=%s", (role_title, description, city, req_students, opp_id))
        conn.commit()
        success = True
    except: success = False
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
        FROM Job_application JA JOIN Application A ON JA.ApplicationID = A.ApplicationID JOIN Student S ON JA.StudentID = S.StudentID WHERE JA.OppID = %s;
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
        FROM Job_application JA JOIN Application A ON JA.ApplicationID = A.ApplicationID JOIN Student S ON JA.StudentID = S.StudentID WHERE A.ApplicationID = %s
    """
    cursor.execute(sql, (app_id,))
    student = cursor.fetchone()
    if student:
        if student.get('ReliabilityScore'): student['ReliabilityScore'] = float(student['ReliabilityScore'])
        if student.get('AvgImpact') and student['AvgImpact'] is not None: student['AvgImpact'] = float(student['AvgImpact'])
        cursor.execute("SELECT Skill FROM SkillTags WHERE StudentID = %s", (student['StudentID'],))
        student['Skills'] = [s['Skill'] for s in cursor.fetchall()]
        
        cursor.execute("SELECT ScheduledTime FROM Interview WHERE ApplicationID = %s", (app_id,))
        interview = cursor.fetchone()
        if interview and interview['ScheduledTime']:
            student['InterviewTime'] = str(interview['ScheduledTime'])
            
    cursor.close()
    conn.close()
    return student

def mark_opportunity_completed(opp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Opportunity SET Status = 'Completed' WHERE OppID = %s", (opp_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error completing opp: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def accept_application(app_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Accept the student
        cursor.execute("UPDATE Application SET Status = 'Accepted' WHERE ApplicationID = %s", (app_id,))
        
        # 2. Find out which job this was for
        cursor.execute("SELECT OppID FROM Job_application WHERE ApplicationID = %s", (app_id,))
        row = cursor.fetchone()
        
        if row:
            opp_id = row['OppID']
            
            # 3. Check if the job has hit its required number of students
            cursor.execute("""
                SELECT O.RequiredStudents, 
                       (SELECT COUNT(*) FROM Job_application JA JOIN Application A ON JA.ApplicationID = A.ApplicationID WHERE JA.OppID = O.OppID AND A.Status = 'Accepted') as AcceptedCount
                FROM Opportunity O WHERE O.OppID = %s
            """, (opp_id,))
            quota = cursor.fetchone()
            req_students = quota['RequiredStudents'] if quota and quota['RequiredStudents'] else 0
            accepted_count = quota['AcceptedCount'] if quota and quota['AcceptedCount'] else 0
            
            # 4. If the quota is filled, mark the job as 'Assigned' and reject everyone else
            if req_students > 0 and accepted_count >= req_students:
                # FIX IS RIGHT HERE: Changed 'Inactive' to 'Assigned'
                cursor.execute("UPDATE Opportunity SET Status = 'Assigned' WHERE OppID = %s", (opp_id,))
                
                # Reject remaining pending applications
                cursor.execute("UPDATE Application SET Status = 'Rejected' WHERE Status = 'Pending' AND ApplicationID IN (SELECT ApplicationID FROM Job_application WHERE OppID = %s)", (opp_id,))
        
        conn.commit()
        success = True
    except Exception as e:
        print(f"CRITICAL HIRE ERROR: {e}")
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

# NEW: Student Marks Milestone as Done
def submit_milestone_work(milestone_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE MilestoneLedger SET ApprovalStatus = 'Submitted' WHERE MilestoneID = %s", (milestone_id,))
        conn.commit()
        success = True
    except Exception as e:
        print(f"CRITICAL HIRE ERROR: {e}")
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

# NEW: Employer Rejects Milestone Work
def reject_milestone(milestone_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE MilestoneLedger SET ApprovalStatus = 'Pending' WHERE MilestoneID = %s", (milestone_id,))
        conn.commit()
        success = True
    except: success = False
    finally:
        cursor.close()
        conn.close()
    return success

def approve_milestone(milestone_id, opp_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    job_completed = False; app_id = None
    try:
        # Get the payout amount
        cursor.execute("SELECT Payout FROM MilestoneLedger WHERE MilestoneID = %s", (milestone_id,))
        payout_res = cursor.fetchone()
        payout_amount = payout_res['Payout'] if payout_res else 0

        # Approve the milestone
        cursor.execute("UPDATE MilestoneLedger SET ApprovalStatus = 'Approved' WHERE MilestoneID = %s", (milestone_id,))
        
        # INSERT INTO TRANSACTION LEDGER
        tx_hash = hashlib.sha256(f"{milestone_id}_{time.time()}".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO Transaction_Ledger (wallet_id, amount, transaction_type, transaction_hash, milestone_id)
            VALUES (%s, %s, 'Payout', %s, %s)
        """, (opp_id, payout_amount, tx_hash, milestone_id))

        # Check Escrow totals to see if job is Funded
        cursor.execute("SELECT SUM(Payout) as TotalApproved FROM MilestoneLedger WHERE OppID = %s AND ApprovalStatus = 'Approved'", (opp_id,))
        approved_sum = cursor.fetchone()['TotalApproved'] or 0
        
        cursor.execute("SELECT TotalAmount FROM ProjWallet WHERE OppID = %s", (opp_id,))
        wallet_total = cursor.fetchone()['TotalAmount'] or 0
        
        cursor.execute("SELECT JA.ApplicationID FROM Job_application JA JOIN Application A ON JA.ApplicationID = A.ApplicationID WHERE JA.OppID = %s AND A.Status = 'Accepted'", (opp_id,))
        res = cursor.fetchone()
        if res: app_id = res['ApplicationID']

        if float(approved_sum) >= float(wallet_total) and float(wallet_total) > 0:
            cursor.execute("UPDATE Opportunity SET Status = 'Funded' WHERE OppID = %s", (opp_id,))
            job_completed = True
            
        conn.commit()
        return True, job_completed, app_id
    except Exception as e:
        print(f"Approve Error: {e}") 
        return False, False, None
    finally:
        cursor.close()
        conn.close()

def submit_feedback(app_id, reviewer_role, metrics, feedback_text):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        for metric, score in metrics.items():
            cursor.execute("INSERT INTO PerformanceLedger (ApplicationID, ImpactScore, MetricType, ReviewerRole) VALUES (%s, %s, %s, %s)", (app_id, score, metric, reviewer_role))
        if feedback_text:
            cursor.execute("INSERT INTO PerformanceLedger (ApplicationID, ImpactScore, MetricType, ReviewerRole) VALUES (%s, NULL, %s, %s)", (app_id, f"Feedback: {feedback_text}", reviewer_role))
        
        # Calculate & Update the Averages
        cursor.execute("SELECT JA.StudentID, P.EmployerID FROM Job_application JA JOIN Posts P ON JA.OppID = P.OppID WHERE JA.ApplicationID = %s", (app_id,))
        ids = cursor.fetchone()

        if reviewer_role == 'Employer':
            cursor.execute("SELECT AVG(PL.ImpactScore) as new_score FROM PerformanceLedger PL JOIN Job_application JA ON PL.ApplicationID = JA.ApplicationID WHERE JA.StudentID = %s AND PL.ReviewerRole = 'Employer' AND PL.ImpactScore IS NOT NULL", (ids['StudentID'],))
            res = cursor.fetchone()
            if res and res['new_score']: cursor.execute("UPDATE Student SET ReliabilityScore = %s WHERE StudentID = %s", (round(res['new_score'], 1), ids['StudentID']))
        else:
            cursor.execute("SELECT AVG(PL.ImpactScore) as new_score FROM PerformanceLedger PL JOIN Job_application JA ON PL.ApplicationID = JA.ApplicationID JOIN Posts P ON JA.OppID = P.OppID WHERE P.EmployerID = %s AND PL.ReviewerRole = 'Student' AND PL.ImpactScore IS NOT NULL", (ids['EmployerID'],))
            res = cursor.fetchone()
            if res and res['new_score']: cursor.execute("UPDATE Employer SET TrustScore = %s WHERE EmployerID = %s", (round(res['new_score'], 1), ids['EmployerID']))
                
        conn.commit()
        success = True
    except Exception as e:
        print(f"Feedback Error: {e}")
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

def apply_for_job(student_id, opp_id):
    if not get_payment_token(student_id, 'student'):
        return False, "ACTION REQUIRED: You must set up a Payout Method in your Dashboard before you can apply to jobs."
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Job_application WHERE StudentID = %s AND OppID = %s", (student_id, opp_id))
        if cursor.fetchone(): return False, "You have already applied for this role."
        
        cursor.execute("INSERT INTO Application (ApplicationDate, Status) VALUES (CURDATE(), 'Pending')")
        app_id = cursor.lastrowid
        cursor.execute("INSERT INTO Job_application (ApplicationID, OppID, StudentID) VALUES (%s, %s, %s)", (app_id, opp_id, student_id))
        conn.commit()
        success, msg = True, "Application Submitted Successfully!"
    except: success, msg = False, "Database Error."
    finally:
        cursor.close()
        conn.close()
    return success, msg

def get_job_details(opp_id, student_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT O.*, E.BusinessName, E.VerifiedIdentity, E.TrustScore FROM Opportunity O JOIN Posts P ON O.OppID = P.OppID JOIN Employer E ON P.EmployerID = E.EmployerID WHERE O.OppID = %s"
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
            if cursor.fetchone(): job['HasApplied'] = True

        cursor.execute("SELECT MilestoneID, Description, Payout, Deadline, ApprovalStatus FROM MilestoneLedger WHERE OppID = %s", (opp_id,))
        job['Milestones'] = cursor.fetchall()

        cursor.execute("SELECT TotalAmount FROM ProjWallet WHERE OppID = %s", (opp_id,))
        wallet = cursor.fetchone()
        total_escrow = float(wallet['TotalAmount']) if wallet else 0.0

        cursor.execute("SELECT SUM(Payout) as ApprovedTotal FROM MilestoneLedger WHERE OppID = %s AND ApprovalStatus = 'Approved'", (opp_id,))
        approved = cursor.fetchone()['ApprovedTotal'] or 0.0
        job['EscrowRemaining'] = total_escrow - float(approved)

        cursor.execute("SELECT S.FirstName, S.LastName, A.ApplicationID FROM Job_application JA JOIN Application A ON JA.ApplicationID = A.ApplicationID JOIN Student S ON JA.StudentID = S.StudentID WHERE JA.OppID = %s AND A.Status = 'Accepted'", (opp_id,))
        hired = cursor.fetchone()
        job['HiredApplicant'] = hired if hired else None

        job['Feedback'] = []
        if hired:
            cursor.execute("SELECT ReviewerRole, MetricType, ImpactScore FROM PerformanceLedger WHERE ApplicationID = %s", (hired['ApplicationID'],))
            job['Feedback'] = cursor.fetchall()

    cursor.close()
    conn.close()
    return job

def search_opportunities(query):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    term = f"%{query}%"
    sql = "SELECT DISTINCT O.* FROM Opportunity O LEFT JOIN RequiredSkills RS ON O.OppID = RS.OppID WHERE O.Status = 'Active' AND (O.RoleTitle LIKE %s OR RS.Skill LIKE %s OR O.City LIKE %s);"
    cursor.execute(sql, (term, term, term))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results