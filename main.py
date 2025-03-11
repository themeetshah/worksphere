from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory, current_app, send_file
from database.db_connection import fetch_query, execute_query, get_user_role
from team_management import create_team, assign_user_to_team, get_team_details, get_all_teams, remove_user_from_team
import matplotlib.pyplot as plt
import numpy as np
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'py', 'html', 'sql'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs("uploads", exist_ok=True)

app = Flask(__name__)
app.secret_key = "1952"

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "", 8)
        self.cell(0, 10, f"WorkSphere | Page {self.page_no()}", align="C")

# ------------------------- Report PDF Generation -------------------------

def generate_project_report(project_id):
    project_query = "SELECT users.name as assigned_name, projects.name, description, client, budget, status, created_at, teams.name as team_name, projects.team_id FROM projects JOIN users ON users.user_id=projects.created_by JOIN teams ON projects.team_id=teams.team_id WHERE project_id = %s"
    project = fetch_query(project_query, (project_id,))[0]
    if project['status'] != 'Completed':
        return "Report generation is only available for completed projects."

    manager_query = """
        SELECT users.name, users.email, users.user_id FROM users JOIN teams WHERE teams.team_id = %s AND users.role = 'Manager'
    """
    manager = fetch_query(manager_query, (project['team_id'],))
    manager_name = manager[0]['name'] if manager else "Not Assigned"
    manager_email = manager[0]['email'] if manager else "Not Assigned"
    manager_id = manager[0]['user_id'] if manager else 0

    team_query = """
        SELECT name, role, email, user_id FROM users WHERE team_id = %s
    """
    team_members = fetch_query(team_query, (project['team_id'],))

    task_query = """
        SELECT task_name, name, deadline, submission FROM tasks JOIN users on users.user_id=tasks.assigned_to WHERE project_id = %s
    """
    tasks = fetch_query(task_query, (project_id,))
    
    team_task_stats = fetch_query("""
        SELECT 
            COUNT(*) AS total_tasks,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'Completed' AND submission <= deadline THEN 1 ELSE 0 END) AS on_time,
            SUM(CASE WHEN status = 'Completed' AND submission > deadline THEN 1 ELSE 0 END) AS `delayed`
            FROM teams t
            LEFT JOIN tasks ts ON t.team_id = ts.team_id
            WHERE ts.project_id = %s
            GROUP BY t.team_id, t.name
        """, (project_id,))

    expense_query = """
        SELECT name, category, amount, description, date, approved FROM expenses JOIN users ON users.user_id=expenses.user_id WHERE project_id = %s
    """
    expenses = fetch_query(expense_query, (project_id,))

    poll_query = """
        SELECT poll_id, question, created_at, closes_at FROM polls WHERE project_id = %s
    """
    polls = fetch_query(poll_query, (project_id,))

    poll_votes_query = """
        SELECT * FROM polls JOIN users ON users.user_id=polls.created_by WHERE project_id = %s
    """
    polls = fetch_query(poll_votes_query, (project_id,))

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 📌 **Page 1: Cover Page**
    pdf.add_page()
    pdf.set_font("Times", "B", 30)
    pdf.cell(200, 10, "WorkSphere", ln=True, align="C")
    
    pdf.ln(60)
    pdf.set_font("Times", "B", 20)
    pdf.cell(200, 10, f"Project Report", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Times", "", 15)
    
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Name", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, project['name'], 1, 1, "L", 1)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Description", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, project['description'], 1, 1, "L", 1)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Client", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, project['client'], 1, 1, "L", 1)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Budget", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, "Rs."+str(project['budget']), 1, 1, "L", 1)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Assigned By", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, project['assigned_name'], 1, 1, "L", 1)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Assigned At", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, project['created_at'].strftime("%d-%m-%Y %H:%M:%S"), 1, 1, "L", 1)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Assigned To", 1, 0, "L", 1)
    pdf.set_fill_color(255, 255, 255)  
    pdf.cell(150, 8, project['team_name'], 1, 1, "L", 1)
    
    # 📌 **Page 2: Manager & Team Details**
    pdf.add_page()
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Manager Details:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.ln(5)
    pdf.set_fill_color(200, 200, 200)
    
    pdf.cell(10, 8, "ID", 1, 0, "C", 1)
    pdf.cell(40, 8, "Name", 1, 0, "C", 1)
    pdf.cell(60, 8, "Email", 1, 0, "C", 1)
    pdf.ln(8)
    
    pdf.set_fill_color(255, 255, 255)
    
    pdf.cell(10, 8, str(manager_id), 1, 0, "C")
    pdf.cell(40, 8, manager_name, 1, 0, "C")
    pdf.cell(60, 8, manager_email, 1, 0, "C")
    
    pdf.ln(28)
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Team Members:", ln=True, align="L")
    pdf.set_font("Times", "", 12)
    pdf.ln(5)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(10, 8, "ID", 1, 0, "C", 1)
    pdf.cell(40, 8, "Name", 1, 0, "C", 1)
    pdf.cell(60, 8, "Email", 1, 0, "C", 1)
    pdf.cell(40, 8, "Role", 1, 1, "C", 1)
    
    pdf.set_fill_color(255, 255, 255)

    for i in range(len(team_members)):
        pdf.cell(10, 8, str(team_members[i]['user_id']), 1, 0, "C")
        pdf.cell(40, 8, team_members[i]['name'], 1, 0, "C")
        pdf.cell(60, 8, team_members[i]['email'], 1, 0, "C")
        pdf.cell(40, 8, team_members[i]['role'], 1, 1, "C")

    # 📌 **Page 3: Task Details & Pie Chart**
    pdf.add_page()
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Task Details", ln=True)
    pdf.set_font("Times", "", 12)
    
    pdf.ln(5)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(40, 8, "Task Name", 1, 0, "C", 1)
    pdf.cell(40, 8, "Assigned To", 1, 0, "C", 1)
    pdf.cell(40, 8, "Deadline", 1, 0, "C", 1)
    pdf.cell(40, 8, "Submission", 1, 1, "C", 1)
    pdf.set_fill_color(255, 255, 255)
    for task in tasks:
        pdf.cell(40, 8, task['task_name'], 1, 0, "C")
        pdf.cell(40, 8, task['name'], 1, 0, "C")
        pdf.cell(40, 8, task['deadline'].strftime("%Y-%m-%d"), 1, 0, "C")
        pdf.cell(40, 8, task['submission'].strftime("%Y-%m-%d"), 1, 1, "C")

    pdf.ln(20)
    
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Task Timing Performance:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.ln(5)
    
    fig = plt.figure(figsize=(6, 4), dpi=100)
    plt.subplot(1,2,1)
    task_statuses = [task['submission'] for task in tasks]
    status_counts = {status: task_statuses.count(status) for status in set(task_statuses)}    
    plt.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', startangle=90)
    labels2 = ["On-Time", "Delayed"]
    sizes2 = [team_task_stats[0]["on_time"], team_task_stats[0]["delayed"]]
    colors2 = ["lightblue", "orange"]

    plt.subplot(1,2,2)
    plt.pie(sizes2, labels=labels2, autopct="%1.1f%%", colors=colors2, startangle=180)
    
    plt.tight_layout()
    timing_chart_url = f"static/reports/graphs/team_task_stats_timing_{project_id}.png"
    fig.savefig(timing_chart_url, bbox_inches='tight')
    pdf.image(timing_chart_url, x=10, w=190)
    plt.close(fig)
    
    # 📌 **Page 4: Expense Details**
    pdf.add_page()
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Expense Details:", ln=True)
    pdf.set_font("Times", "", 12)
    
    pdf.ln(5)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(30, 8, "Name", 1, 0, "C", 1)
    pdf.cell(30, 8, "Category", 1, 0, "C", 1)
    pdf.cell(30, 8, "Amount", 1, 0, "C", 1)
    pdf.cell(30, 8, "Description", 1, 0, "C", 1)
    pdf.cell(30, 8, "Date", 1, 0, "C", 1)
    pdf.cell(30, 8, "Approved?", 1, 1, "C", 1)
    pdf.set_fill_color(255, 255, 255)
    for expense in expenses:
        pdf.cell(30, 8, expense['name'], 1, 0, "C")
        pdf.cell(30, 8, expense['category'], 1, 0, "C")
        pdf.cell(30, 8, "Rs."+str(expense['amount']), 1, 0, "C")
        pdf.cell(30, 8, expense['description'], 1, 0, "C")
        pdf.cell(30, 8, expense['date'].strftime("%Y-%m-%d"), 1, 0, "C")
        pdf.cell(30, 8, expense['approved'], 1, 1, "C")
        
    pdf.ln(20)
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Expense Breakdown:", ln=True)
    pdf.set_font("Times", "", 12)
    budget_query = "SELECT budget FROM projects WHERE project_id = %s"
    project_data = fetch_query(budget_query, (project_id,))
    if not project_data:
        return None
    
    total_budget = float(project_data[0]['budget'])

    query = """
        SELECT category, SUM(amount) AS total 
        FROM expenses WHERE project_id = %s AND approved = 'Approved' 
        GROUP BY category
    """
    data = fetch_query(query, (project_id,))
    print("253:", data)
    
    categories = [row['category'] for row in data]
    amounts = [row['total'] for row in data]
    total_expenses = float(sum(amounts))
    budget_left = max(total_budget - total_expenses, 0)
    categories.append("Budget Left")
    amounts.append(budget_left)
    
    fig = plt.figure(figsize=(6, 4), dpi=100)
    plt.pie(amounts, labels=categories, autopct='%1.2f%%')
    chart_url = f"static/reports/graphs/expenses_pie_{project_id}.png"
    fig.savefig(chart_url, bbox_inches='tight')
    pdf.image(chart_url, x=20, w=100)
    plt.close(fig)

    # 📌 **Page 5: Polls & Poll Results Graph**
    pdf.add_page()
    pdf.set_font("Times", "B", 20)
    pdf.cell(0, 10, "Polls:", ln=True)
    pdf.set_font("Times", "", 12)
    pdf.ln(5)
    
    for i in range(len(polls)):
        poll_id = polls[i]['poll_id']
        pdf.cell(0, 8, f"Poll {i+1}:", ln=True)
        pdf.cell(0, 8, f"Question: {polls[i]['question']}", ln=True)
        pdf.cell(0, 8, f"Created By: {polls[i]['name']}", ln=True)
        pdf.cell(0, 8, f"Created At: {polls[i]['created_at']}", ln=True)
        pdf.cell(0, 8, f"Closing At: {polls[i]['closes_at']}", ln=True)

        poll_info_query = "SELECT question FROM polls WHERE poll_id = %s"
        poll_info = fetch_query(poll_info_query, (poll_id,))[0]

        options_query = """
            SELECT po.option_text, COUNT(pv.vote_id) AS votes
            FROM poll_options po
            LEFT JOIN poll_votes pv ON po.option_id = pv.option_id
            WHERE po.poll_id = %s
            GROUP BY po.option_text
        """
        options = fetch_query(options_query, (poll_id,))

        labels = [opt['option_text'] for opt in options]
        votes = [opt['votes'] for opt in options]

        fig = plt.figure(figsize=(8, 4))
        plt.barh(labels, votes, color='skyblue')
        plt.xlabel('Votes')
        plt.ylabel('Options')
        plt.title(poll_info['question'])

        chart_url = f"static/reports/graphs/poll_result_{poll_id}.png"
        fig.savefig(chart_url, bbox_inches='tight')
        pdf.image(chart_url, x=20, w=100)
        plt.close()
        pdf.ln(10)
    file_path = f"static/reports/project_report_{project_id}.pdf"
    pdf.output(file_path)
    return file_path

@app.route('/download_report/<int:project_id>')
def download_report(project_id):
    file_path = generate_project_report(project_id)
    return send_file(file_path, as_attachment=True)

# ------------------------- Basic Routes -------------------------

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    debug_logs = []
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = fetch_query("SELECT user_id, name, role FROM users WHERE email = %s AND password = %s", (email, password))

        if user:
            session['user_id'] = user[0]['user_id']
            session['name'] = user[0]['name']
            session['role'] = user[0]['role']
            print(session)
            return redirect('/dashboard')
        else:
            flash('❌ Invalid email or password.', 'danger')
            return redirect('/login')
    return render_template('login.html', debug_logs=debug_logs)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', name=session['name'], role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ------------------------- Profile Management Routes -------------------------

@app.route('/profile', defaults={'user_id': None})
@app.route('/profile/<int:user_id>')
def profile(user_id):
    session_user_id = session.get('user_id')
    
    if not session_user_id:
        return redirect(url_for('login'))

    if user_id is None:
        user_id = session_user_id

    user = fetch_query("SELECT name, user_id, email, role, team_id FROM users WHERE user_id = %s", (user_id,))
    if not user:
        flash("User not found!", "danger")
        return redirect('/employees')

    user = user[0]

    if user['role'] == 'Manager':
        projects_managed = fetch_query("""
            SELECT p.project_id, p.name, p.status, p.client 
        FROM projects p
        JOIN teams t ON p.team_id = t.team_id
        WHERE t.manager_id = %s
        """, (user_id,))

        teams_under = fetch_query("""
            SELECT team_id, name FROM teams WHERE manager_id = %s
        """, (user_id,))

        team_task_stats = fetch_query("""
            SELECT 
                t.team_id, t.name,
                COUNT(ts.task_id) AS total_tasks,
                SUM(CASE WHEN ts.status = 'Completed' AND ts.submission <= ts.deadline THEN 1 ELSE 0 END) AS tasks_on_time
            FROM teams t
            LEFT JOIN tasks ts ON t.team_id = ts.team_id
            WHERE t.manager_id = %s
            GROUP BY t.team_id, t.name
        """, (user_id,))
        
        if team_task_stats:
            team_names = [team['name'] for team in team_task_stats]
            total_tasks = np.array([team['total_tasks'] for team in team_task_stats])
            on_time_tasks = np.array([team['tasks_on_time'] for team in team_task_stats])

            fig = plt.figure(figsize=(6, 4), dpi=100)
            plt.bar(team_names, total_tasks, width=0.4, label='Total Tasks', color='lightgray')
            plt.bar(team_names, on_time_tasks, width=0.4, label='On-Time Tasks', color='green')

            plt.xlabel('Teams')
            plt.ylabel('Number of Tasks')
            plt.title(f"Team Task Performance (Manager ID : {user_id})")
            plt.legend()
            plt.grid(axis='y')
            plt.xticks(rotation=20)

            chart_url = f"teams_task_stats_{user_id}.png"
            fig.savefig(f"static/{chart_url}", bbox_inches='tight')
            plt.close(fig)
        else:
            chart_url = None

        return render_template(
            'profile.html',
            user=user,
            projects_managed=projects_managed,
            teams_under=teams_under,
            team_task_stats=team_task_stats,
            chart_url=chart_url,
            is_manager=True
        )

    elif user['role'] == 'Owner':
        total_projects = fetch_query("SELECT COUNT(*) AS total FROM projects", ())
        total_projects = total_projects[0]['total'] if total_projects else 0

        distinct_clients = fetch_query("SELECT COUNT(DISTINCT client) AS total_clients FROM projects", ())
        distinct_clients = distinct_clients[0]['total_clients'] if distinct_clients else 0
        
        total_employees = fetch_query("SELECT COUNT(*) AS total_employees FROM users")
        total_employees = total_employees[0]['total_employees'] if total_employees else 0

        return render_template(
            'profile.html',
            user=user,
            total_employees = total_employees,
            total_projects=total_projects,
            distinct_clients=distinct_clients,
            is_owner=True
        )

    else:
        projects = fetch_query("""
            SELECT DISTINCT p.project_id, p.name, p.status, p.client 
            FROM projects p
            LEFT JOIN users u ON p.team_id = u.team_id AND u.user_id = %s
            LEFT JOIN tasks t ON p.project_id = t.project_id AND t.assigned_to = %s
            WHERE u.user_id IS NOT NULL OR t.assigned_to IS NOT NULL
        """, (user_id, user_id))
        
        hours = fetch_query("""SELECT * FROM working_hours WHERE user_id=%s""", (user_id,))

        weekly_data = {}
        monthly_data = {}
        
        weekly_chart_url=""
        monthly_chart_url=""
        
        print("scsa:",hours, len(hours))
        if len(hours)!=0:
            for hour in hours:
                date = hour['date']
                hours_worked = int(hour['hours'])
                
                week_number = date.isocalendar()[1]
                month_number = date.month
                
                if week_number not in weekly_data:
                    weekly_data[week_number] = 0
                if month_number not in monthly_data:
                    monthly_data[month_number] = 0
                
                weekly_data[week_number] += hours_worked
                monthly_data[month_number] += hours_worked
                
            print(weekly_data, monthly_data)
            sorted_weekly_data = sorted(weekly_data.items())
            sorted_monthly_data = sorted(monthly_data.items())

            weeks, weekly_hours = zip(*sorted_weekly_data)

            fig_weekly = plt.figure(figsize=(6, 4), dpi=100)
            plt.bar(weekly_hours, weeks, color='lightblue')

            plt.xlabel('Week')
            plt.ylabel('Working Hours')
            plt.title(f"Weekly Working Hours (User ID: {user_id})")
            plt.grid(axis='y')

            weekly_chart_url = f"weekly_working_hours_{user_id}.png"
            fig_weekly.savefig(f"static/{weekly_chart_url}", bbox_inches='tight')
            plt.close(fig_weekly)

            months, monthly_hours = zip(*sorted_monthly_data)
            labels = [f"Month {m}\n{h} hrs" for m, h in zip(months, monthly_hours)]

            fig_monthly = plt.figure(figsize=(6, 4), dpi=100)
            plt.pie(monthly_hours, labels=labels, autopct='%1.1f%%')

            plt.title(f"Monthly Working Hours (User ID: {user_id})")

            monthly_chart_url = f"monthly_working_hours_{user_id}.png"
            fig_monthly.savefig(f"static/{monthly_chart_url}", bbox_inches='tight')
            plt.close(fig_monthly)
            
        total_tasks = fetch_query("SELECT COUNT(*) AS total_tasks FROM tasks WHERE assigned_to = %s", (user_id,))
        total_tasks = total_tasks[0]['total_tasks'] if total_tasks else 0
        
        completed_before_deadline = fetch_query("""
            SELECT COUNT(*) AS completed_before_deadline
            FROM tasks WHERE assigned_to = %s AND status = 'Completed' AND submission <= deadline
        """, (user_id,))
        completed_before_deadline = completed_before_deadline[0]['completed_before_deadline'] if completed_before_deadline else 0

        completed_after_deadline = fetch_query("""
            SELECT COUNT(*) AS completed_after_deadline
            FROM tasks WHERE assigned_to = %s AND status = 'Completed' AND submission > deadline
        """, (user_id,))
        completed_after_deadline = completed_after_deadline[0]['completed_after_deadline'] if completed_after_deadline else 0

        return render_template(
            'profile.html',
            user=user,
            projects=projects,
            total_tasks=total_tasks,
            completed_before_deadline=completed_before_deadline,
            completed_after_deadline=completed_after_deadline,
            weekly_chart_url=weekly_chart_url,
            monthly_chart_url=monthly_chart_url
        )

# ------------------------- Team Management Routes -------------------------

@app.route('/teams')
def view_teams():
    if 'user_id' not in session:
        return redirect('/login')
    debug_logs = []
    if get_user_role(session['user_id']) not in ["Owner", "Manager", "Team Leader", "Team Member"]:
        debug_logs.append("❌ You do not have permission to view teams.")
        session['debug_logs'] = debug_logs
        debug_logs = session.pop('debug_logs', [])
        return render_template('dashboard.html', debug_logs=debug_logs)
    
    teams = get_all_teams(session['user_id'])
    debug_logs = session.pop('debug_logs', [])
    session['debug_logs'] = debug_logs
    debug_logs = session.pop('debug_logs', [])
    return render_template('teams.html', teams=teams, role=session['role'], debug_logs=debug_logs)

@app.route('/add_team', methods=['GET', 'POST'])
def add_team():
    if 'user_id' not in session:
        return redirect('/login')

    debug_logs = []

    if request.method == 'GET':
        managers = fetch_query (
            "SELECT user_id, name FROM users WHERE role = 'Manager';"
        )
        return render_template('add_team.html', managers=managers, debug_logs=debug_logs, role=session['role'], name=session['name'], user_id=session['user_id'])

    elif request.method == 'POST':
        name = request.form['name']
        manager_id = request.form['manager_id']

        existing_team = fetch_query("SELECT * FROM teams WHERE name = %s", (name,))
        if existing_team:
            debug_logs.append("❌ Team name already exists. Choose a different name.")
        else:
            execute_query("INSERT INTO teams (name, manager_id) VALUES (%s, %s)", (name, manager_id))
            debug_logs.append("✅ Team created successfully!")

        session['debug_logs'] = debug_logs
        return redirect('/teams')

    debug_logs = session.pop('debug_logs', [])
    return render_template('add_team.html', debug_logs=debug_logs)

@app.route('/team_details/<int:team_id>')
def team_details(team_id):
    if 'user_id' not in session:
        return redirect('/login')

    members = fetch_query("SELECT user_id, name, email, role FROM users WHERE team_id = %s", (team_id,))

    team_task_stats = fetch_query("""
        SELECT 
            COUNT(*) AS total_tasks,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'Completed' AND submission <= deadline THEN 1 ELSE 0 END) AS on_time,
            SUM(CASE WHEN status = 'Completed' AND submission > deadline THEN 1 ELSE 0 END) AS `delayed`
        FROM tasks WHERE team_id = %s
    """, (team_id,))
    
    completion_chart_url, timing_chart_url = None, None
    if team_task_stats[0]['total_tasks']>0:
        if team_task_stats[0]["completed"] > 0 or team_task_stats[0]["pending"] > 0:
            labels1 = ["Completed", "Pending"]
            sizes1 = [team_task_stats[0]["completed"], team_task_stats[0]["pending"]]
            colors1 = ["green", "red"]

            fig1= plt.figure(figsize=(5, 5), dpi=100)
            plt.pie(sizes1, labels=labels1, autopct="%1.1f%%", colors=colors1, startangle=90)
            plt.title("Task Completion Status")
            plt.legend()

            completion_chart_url = f"team_task_stats_completion_{team_id}.png"
            fig1.savefig(f"static/{completion_chart_url}", bbox_inches='tight')
            plt.close(fig1)
            
        if team_task_stats[0]["on_time"] > 0 or team_task_stats[0]["delayed"] > 0:
            labels2 = ["On-Time", "Delayed"]
            sizes2 = [team_task_stats[0]["on_time"], team_task_stats[0]["delayed"]]
            colors2 = ["lightblue", "orange"]

            fig2 = plt.figure(figsize=(5, 5), dpi=100)
            plt.pie(sizes2, labels=labels2, autopct="%1.1f%%", colors=colors2, startangle=90)
            plt.title("Task Timing Performance")
            plt.legend()
            
            timing_chart_url = f"team_task_stats_timing_{team_id}.png"
            fig2.savefig(f"static/{timing_chart_url}", bbox_inches='tight')
            plt.close(fig2)
                
    completed_projects = fetch_query("SELECT name, project_id, client, status FROM projects WHERE team_id = %s AND status = 'Completed'", (team_id,))

    ongoing_projects = fetch_query("SELECT project_id, name, status, client FROM projects WHERE team_id = %s AND status IN ('In Progress', 'Pending')", (team_id,))

    return render_template(
        'team_details.html',
        team_id=team_id,
        members=members,
        team_task_stats=team_task_stats,
        completed_projects=completed_projects,
        ongoing_projects=ongoing_projects,
        completion_chart_url=completion_chart_url,
        timing_chart_url=timing_chart_url
    )

@app.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    debug_logs = []

    members = get_team_details(team_id, user_id)

    if members and members[0] == "Can't":
        debug_logs.append("⚠️ You don't have permission to edit this team.")
        session['debug_logs'] = debug_logs
        return redirect('/teams')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == "add":
            new_user_id = request.form.get('new_user_id')
            new_role = request.form.get('new_role')
            success, logs = assign_user_to_team(new_user_id, team_id, new_role)
            debug_logs.extend(logs)

        elif action == "remove":
            selected_user_id = int(request.form.get('user_id'))
            success, logs = remove_user_from_team(selected_user_id, team_id)
            debug_logs.extend(logs)

        session['debug_logs'] = debug_logs
        return redirect(url_for('edit_team', team_id=team_id))

    debug_logs = session.pop('debug_logs', [])
    return render_template('edit_team.html', team_id=team_id, members=members, debug_logs=debug_logs)

# ------------------------- Employee Management Routes -------------------------

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] not in ['Manager', 'Owner']:
        flash("❌ You don't have permission to view employees.", "danger")
        return redirect('/dashboard')

    employees = fetch_query("SELECT user_id, name, email, role FROM users", ())

    return render_template('employees.html', employees=employees)

@app.route('/add_employees', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect('/login')

    debug_logs = []

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        try:
            existing_user = fetch_query("SELECT user_id FROM users WHERE email = %s", (email,))
            if existing_user:
                debug_logs.append("❌ Employee with this email already exists.")
            else:
                execute_query("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                              (name, email, password, role))
                debug_logs.append("✅ Employee added successfully!")
        except Exception as e:
            debug_logs.append(f"⚠️ Error: {str(e)}")

    return render_template('add_employees.html', debug_logs=debug_logs)

# ------------------------- Task Management Routes -------------------------

@app.route('/assign_task/<int:project_id>', methods=['GET', 'POST'])
def assign_task(project_id):
    user_id = session.get('user_id')
    role = session.get('role')

    if role not in ['Owner', 'Manager', 'Team Leader']:
        flash("You don't have permission to assign tasks.", "danger")
        return redirect(url_for('dashboard'))

    if request.method=='GET':
        team_query = """
            SELECT DISTINCT team_id FROM users WHERE user_id = %s
        """
        user_teams = fetch_query(team_query, (user_id,))

        if not user_teams:
            flash("You are not assigned to any team.", "warning")
            return redirect(url_for('dashboard'))

        team_ids = tuple(team['team_id'] for team in user_teams)

        if len(team_ids) == 1:
            projects_query = "SELECT project_id, name FROM projects WHERE team_id = %s"
            projects = fetch_query(projects_query, (team_ids[0],))
        else:
            projects_query = f"SELECT project_id, name FROM projects WHERE team_id IN {team_ids}"
            projects = fetch_query(projects_query)

        if team_ids:
            team_ids_str = f"({','.join(map(str, team_ids))})"
        else:
            team_ids_str = "(NULL)" 

        team_users_query = f"""
            SELECT u.user_id, u.name 
            FROM users u 
            WHERE u.team_id IN {team_ids_str}
        """
        team_users = fetch_query(team_users_query)
        return render_template('assign_task.html', projects=projects, team_users=team_users, project_id=project_id)
    
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        assigned_to = request.form['assigned_to']
        due_date = request.form['due_date']
        project_id = request.form['project_id']

        if not (assigned_to and title and due_date):
            flash("All fields are required!", "danger")
            return redirect(url_for('assign_task', project_id=project_id))

        team_id = fetch_query("SELECT team_id FROM users WHERE user_id = %s", (assigned_to,))
        if not team_id:
            flash("Invalid user selection!", "danger")
            return redirect(url_for('assign_task', project_id=project_id))
        try:
            print(title, description, assigned_to, due_date, project_id)
            execute_query("""
                INSERT INTO tasks (task_name, description, assigned_to, deadline, team_id, project_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
            """, (title, description, assigned_to, due_date, team_id[0]['team_id'], project_id))

            flash("Task assigned successfully!", "success")
            return redirect(url_for('tasks', project_id=project_id))
        except Exception as E:
            flash("Error assigning task!", "danger")
            print(title, description, assigned_to, due_date, project_id)
            print(E)
            return redirect(url_for('assign_task', project_id=project_id))

@app.route('/tasks', defaults={'project_id': None})
@app.route('/tasks/<int:project_id>')
def tasks(project_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    role = session['role']
    
    if role == 'Owner':
        task_list = fetch_query("SELECT tasks.*, projects.name as project_name, users.name as name FROM tasks LEFT JOIN projects ON tasks.project_id=projects.project_id LEFT JOIN users ON tasks.assigned_to = users.user_id WHERE tasks.project_id=%s", (project_id,))
        members = fetch_query("SELECT * FROM users where role IN ('Team Leader', 'Team Member')")
        projects_query = "SELECT * FROM projects"
        projects = fetch_query(projects_query)
        
    elif role == 'Manager':
        task_list = fetch_query("SELECT tasks.*, projects.name as project_name, users.name as name FROM tasks LEFT JOIN projects ON tasks.project_id=projects.project_id LEFT JOIN users ON tasks.assigned_to = users.user_id WHERE tasks.team_id IN (SELECT team_id FROM teams WHERE manager_id = %s) and tasks.project_id=%s", (user_id,project_id,))
        members = fetch_query("SELECT * FROM users LEFT JOIN teams ON teams.team_id = users.user_id WHERE manager_id = %s", (user_id,))
        projects_query = """
            SELECT * FROM projects 
            WHERE team_id IN (SELECT team_id FROM teams WHERE manager_id = %s) AND project_id=%s
        """
        projects = fetch_query(projects_query, (user_id,project_id,)) 
        
    else:
        task_list = fetch_query("SELECT tasks.*, projects.name as project_name, users.name as name FROM tasks LEFT JOIN projects ON tasks.project_id=projects.project_id LEFT JOIN users ON tasks.assigned_to = users.user_id WHERE tasks.team_id = (SELECT team_id FROM users WHERE user_id = %s) and tasks.project_id=%s", (user_id,project_id,))
        members = fetch_query("SELECT * FROM users user_id WHERE team_id = (SELECT team_id FROM users WHERE user_id = %s)", (user_id,))
        projects_query = "SELECT * FROM projects WHERE team_id IN (SELECT team_id FROM users WHERE user_id = %s) and project_id=%s"
        projects = fetch_query(projects_query, (user_id,project_id,)) 
        
    print("848: ",projects)
    return render_template('tasks.html', tasks=task_list, team_members=members, projects=projects[0])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/submit_task/<int:task_id>', methods=['POST'])
def submit_task(task_id):
    if 'user_id' not in session:
        flash("You must be logged in to submit a task.", "danger")
        print("You must be logged in to submit a task.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    task = fetch_query("SELECT assigned_to, status, project_id FROM tasks WHERE task_id = %s", (task_id,))
    print("870:",task)
    
    if not task:
        flash("Task not found!", "danger")
        print("Task not found!", "danger")
        return redirect(url_for('projects_page'))

    assigned_to, status, project_id = task[0]['assigned_to'], task[0]['status'], task[0]['project_id']

    if assigned_to != user_id:
        flash("You can only submit tasks assigned to you!", "warning")
        print("You can only submit tasks assigned to you!", "warning")
        return redirect(url_for('tasks', project_id=project_id))

    if status == "Completed":
        flash("Task has already been submitted!", "info")
        print("Task has already been submitted!", "info")
        return redirect(url_for('tasks', project_id=project_id))

    if 'file' not in request.files:
        flash("No file uploaded!", "danger")
        print("No file uploaded!", "danger")
        return redirect(url_for('tasks', project_id=project_id))

    file = request.files['file']

    if file.filename == '':
        flash("No selected file!", "danger")
        print("No selected file!", "danger")
        return redirect(url_for('tasks', project_id=project_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads/', filename)
        file.save(file_path)

        execute_query(
            "UPDATE tasks SET status = 'Completed', submission_file = %s, submission = NOW() WHERE task_id = %s",
            (file_path, task_id)
        )
        
        flash("Task submitted successfully!", "success")
        print("Task submitted successfully!", "success")
        return redirect(url_for('tasks', project_id=project_id))
    
    flash("Invalid file format!", "danger")
    print("Invalid file format!", "danger")
    return redirect(url_for('tasks', project_id=project_id))

@app.route('/download/<filename>')
def download_file(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        flash("File not found!", "danger")
        return redirect(request.referrer or url_for('tasks'))

    return send_from_directory(upload_folder, filename, as_attachment=True)

@app.route('/projects', methods=['GET', 'POST'])
def projects_page():
    user_id = session.get('user_id')
    role = session.get('role')

    if role == 'Owner':
        projects = fetch_query("""
            SELECT DISTINCT p.*, t.name as team_name FROM projects p
            JOIN teams t ON p.team_id = t.team_id
            """, ())
        teams = fetch_query("SELECT * FROM teams")

    elif role == 'Manager':
        projects = fetch_query("""
            SELECT DISTINCT p.*, t.name as team_name FROM projects p
            JOIN teams t ON p.team_id = t.team_id
            WHERE t.manager_id = %s
        """, (user_id,))
        teams = fetch_query("SELECT * FROM teams WHERE manager_id = %s", (user_id,))

    elif role in ['Team Leader', 'Team Member']:
        projects = fetch_query("""
            SELECT DISTINCT p.*, t.name as team_name FROM projects p
            JOIN teams t ON p.team_id = t.team_id
            JOIN users u ON t.team_id = u.team_id
            WHERE u.user_id = %s
        """, (user_id,))
        teams = []

    else:
        projects = []
        teams = []

    return render_template('projects.html', projects=projects, teams=teams)

@app.route('/add_project', methods=['POST'])
def add_project():
    if session.get('role') not in ['Owner', 'Manager']:
        flash("You don't have permission to add a project.", "danger")
        return redirect(url_for('projects_page'))

    name = request.form.get('name')
    description = request.form.get('description')
    client = request.form.get('client')
    budget = request.form.get('budget')
    team_id = request.form.get('team_id')
    created_by = session.get('user_id')

    query = """
    INSERT INTO projects (name, description, client, budget, team_id, created_by, created_at, status)
    VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'Pending')
    """
    execute_query(query, (name, description, client, budget, team_id, created_by))
    
    flash("Project added successfully!", "success")
    return redirect(url_for('projects_page'))

@app.route('/submit_project/<int:project_id>', methods=['POST'])
def submit_project(project_id):
    if session.get('role') != 'Team Leader':
        flash("Only Team Leaders can submit projects.", "danger")
        return redirect(url_for('projects_page'))

    query = "SELECT COUNT(*) FROM tasks WHERE project_id = %s AND status != 'Completed'"
    remaining_tasks = fetch_query(query, (project_id,))[0]['COUNT(*)']
    print(remaining_tasks)
    if remaining_tasks > 0:
        flash("All tasks must be completed before submitting the project!", "danger")
        return redirect(url_for('projects_page'))

    update_query = "UPDATE projects SET status = 'Completed' WHERE project_id = %s"
    execute_query(update_query, (project_id,))

    flash("Project submitted successfully!", "success")
    return redirect(url_for('projects_page'))

# ------------------------- Expense Management Routes -------------------------

def generate_expense_pie_chart(project_id):
    budget_query = "SELECT budget FROM projects WHERE project_id = %s"
    project_data = fetch_query(budget_query, (project_id,))
    print(project_data)
    if not project_data:
        return None
    
    total_budget = float(project_data[0]['budget'])
    print(total_budget)

    query = """
        SELECT category, SUM(amount) AS total 
        FROM expenses WHERE project_id = %s AND approved = 'Approved' 
        GROUP BY category
    """
    data = fetch_query(query, (project_id,))
    
    if not data:
        return None

    categories = [row['category'] for row in data]
    amounts = [row['total'] for row in data]
    
    total_expenses = float(sum(amounts))

    budget_left = max(total_budget - total_expenses, 0)
    
    categories.append("Budget Left")
    amounts.append(budget_left)
    
    fig = plt.figure(figsize=(6, 4), dpi=100)
    plt.pie(amounts, labels=categories, autopct='%1.2f%%')
    plt.title("Expense Breakdown")
    plt.legend(loc='upper right', frameon=True, bbox_to_anchor=(1,1))

    chart_url = f"expenses_pie_{project_id}.png"
    fig.savefig(f"static/{chart_url}", bbox_inches='tight')
    plt.close(fig)
    
    return f"static/{chart_url}"

def generate_expense_bar_chart(project_id):
    query = """
        SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
        FROM expenses WHERE approved = 'Approved' and project_id = %s
        GROUP BY month ORDER BY month
    """
    data = fetch_query(query, (project_id,))

    if not data:
        return None

    months = [row['month'] for row in data]
    totals = [row['total'] for row in data]

    fig = plt.figure(figsize=(6, 4), dpi=100)
    plt.bar(months, totals, color='skyblue')
    plt.xlabel("Month")
    plt.ylabel("Total Expenses")
    plt.title("Monthly Expenses")

    chart_url = f"expenses_bar.png"
    fig.savefig(f"static/{chart_url}", bbox_inches='tight')
    plt.close(fig)

    return f"static/{chart_url}"

@app.route('/expenses')
def expenses():
    user_role = session['role']
    user_id = session['user_id']
    
    if user_role == 'Owner':
        query = "SELECT * FROM projects"
        projects = fetch_query(query)

    elif user_role == 'Manager':
        query = """
            SELECT p.* FROM projects p
            JOIN teams t ON p.team_id = t.team_id
            WHERE t.manager_id = %s
        """
        projects = fetch_query(query, (user_id,))
    
    else:
        query = """
            SELECT p.* FROM projects p
            JOIN users u ON p.team_id = u.team_id
            WHERE u.user_id = %s
        """
        projects = fetch_query(query, (user_id,))

    return render_template('expenses_projects.html', projects=projects)

@app.route('/expenses/<int:project_id>', methods=['GET', 'POST'])
def project_expenses(project_id):
    categories = fetch_query("SELECT category FROM expenses WHERE project_id=%s", (project_id,))
    categories = [c['category'] for c in categories]
    
    filters = []
    params = [project_id]
        
    role = session['role']
    if role == 'Owner':
        projects_query = "SELECT * FROM projects"
        
    elif role == 'Manager':
        projects_query = """
            SELECT * FROM projects 
            WHERE team_id IN (SELECT team_id FROM teams WHERE manager_id = %s) AND project_id=%s
        """
    else:
        projects_query = "SELECT * FROM projects WHERE team_id = (SELECT team_id FROM users WHERE user_id = %s) AND project_id=%s"
        
    projects = fetch_query(projects_query, (session['user_id'],project_id,)) if role != 'Owner' else fetch_query(projects_query)
    
    if request.method == 'POST':
        category = request.form.get('category')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        member = request.form.get('member')

        if category:
            filters.append("e.category = %s")
            params.append(category)
        if date_from:
            filters.append("e.date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("e.date <= %s")
            params.append(date_to)
        if member:
            filters.append("u.name LIKE %s")
            params.append(f"%{member}%")

    filter_query = " AND ".join(filters)
    query = f"""
        SELECT e.expense_id, e.amount, e.category, e.description, e.date, e.approved, u.name AS submitted_by, p.name as project_name FROM expenses e JOIN users u ON e.user_id = u.user_id JOIN projects p ON e.project_id = p.project_id WHERE e.project_id = %s {f"AND {filter_query}" if filter_query else ""}
    """
    
    expenses = fetch_query(query, tuple(params))
    
    pie_chart = generate_expense_pie_chart(project_id)
    bar_chart = generate_expense_bar_chart(project_id)
    
    return render_template('expenses.html', expenses=expenses, project_id=project_id, pie_chart=pie_chart, categories=categories, bar_chart=bar_chart, projects=projects[0])

@app.route('/add_expense/<int:project_id>', methods=['GET', 'POST'])
def add_expense(project_id):
    if session['role'] not in ['Team Leader', 'Team Member']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    projects_query = "SELECT * FROM projects WHERE project_id = %s"
    project = fetch_query(projects_query, (project_id,))[0]
        
    if request.method == 'POST':
        project_id = request.form['project_id']
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        date = datetime.today()
        
        project_query = "SELECT * FROM projects WHERE project_id = %s"
        project = fetch_query(project_query, (project_id,))
        
        if not project:
            flash('Invalid project selected!', 'danger')
            return redirect(url_for('expenses'))
        
        project_budget = float(project[0]['budget'])

        total_expense_query = """
            SELECT COALESCE(SUM(amount), 0) AS total_expense
            FROM expenses
            WHERE project_id = %s AND approved = 'Approved'
        """
        total_expense = fetch_query(total_expense_query, (project_id,))
        total_expense = float(total_expense[0]['total_expense'])

        remaining_budget = project_budget - total_expense

        if amount > remaining_budget:
            flash(f'Expense exceeds remaining budget (Rs.{remaining_budget:.2f})!', 'danger')
            return redirect(url_for('expenses'))
    
        insert_query = """
            INSERT INTO expenses (project_id, user_id, amount, category, description, date, approved)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
        """
        execute_query(insert_query, (project_id, session['user_id'], amount, category, description, date))
        flash('Expense submitted for approval!', 'success')
        return redirect(url_for('expenses', project_id=project_id))
    
    print(project)
    return render_template('add_expense.html', project=project)

@app.route('/approve_expense/<int:expense_id>/<status>', methods=['POST'])
def approve_expense(expense_id, status):
    if session['role'] != 'Manager':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('expenses'))

    if status not in ['Approved', 'Rejected']:
        flash('Invalid status!', 'danger')
        return redirect(url_for('expenses'))

    expense_query = "SELECT project_id, amount FROM expenses WHERE expense_id = %s AND approved = 'Pending'"
    expense = fetch_query(expense_query, (expense_id,))
    
    if not expense:
        flash('Expense not found or already processed!', 'danger')
        return redirect(url_for('expenses'))
    
    project_id, expense_amount = expense[0]['project_id'], expense[0]['amount']

    if status == 'Approved':
        project_query = "SELECT budget FROM projects WHERE project_id = %s"
        project = fetch_query(project_query, (project_id,))
        if not project:
            flash('Project not found!', 'danger')
            return redirect(url_for('expenses'))

        project_budget = project[0]['budget']

        total_expense_query = """
            SELECT SUM(amount) AS total FROM expenses 
            WHERE project_id = %s AND approved = 'Approved'
        """
        total_expense = fetch_query(total_expense_query, (project_id,))[0]['total'] or 0

        if total_expense + expense_amount > project_budget:
            flash('Approval failed: Expense exceeds project budget!', 'danger')
            return redirect(url_for('expenses'))

    update_query = "UPDATE expenses SET approved = %s WHERE expense_id = %s AND approved = 'Pending'"
    execute_query(update_query, (status, expense_id))

    flash(f'Expense {status} successfully!', 'success')
    return redirect(url_for('expenses'))

# ------------------------- Poll Management Routes -------------------------

@app.route('/polls')
def poll_projects():
    user_id = session.get('user_id')
    role = session.get('role')

    if role not in ['Team Member', 'Team Leader']:
        flash("You don't have access to polls.", "danger")
        return redirect(url_for('dashboard'))

    query = """
        SELECT projects.* 
        FROM projects
        JOIN users ON projects.team_id = users.team_id
        WHERE users.user_id = %s
    """
    projects = fetch_query(query, (user_id,))

    return render_template('poll_projects.html', projects=projects)

@app.route('/polls/<int:project_id>')
def view_polls(project_id):
    user_id = session['user_id']

    close_expired_polls_query = """
        UPDATE polls SET is_closed = TRUE 
        WHERE closes_at < NOW() AND is_closed = FALSE
    """
    execute_query(close_expired_polls_query)

    polls_query = """
        SELECT polls.*, users.name AS creator_name 
        FROM polls
        JOIN users ON polls.created_by = users.user_id
        WHERE polls.project_id = %s
    """
    polls = fetch_query(polls_query, (project_id,))
    
    projects_query = "SELECT * FROM projects WHERE project_id = %s"
    
    projects = fetch_query(projects_query, (project_id,))
    print(projects)
    return render_template('polls.html', polls=polls, project_id=project_id, projects=projects[0])

@app.route('/create/<int:project_id>', methods=['GET', 'POST'])
def create_poll(project_id):
    user_id = session['user_id']
    
    if request.method == 'POST':
        question = request.form['question']
        closes_at = request.form['closes_at']
        options = request.form.getlist('options')
        
        if not question or not closes_at or len(options) < 2:
            flash("Poll must have a question and at least two options.", "danger")
            return redirect(url_for('create_poll', project_id=project_id))

        poll_query = "INSERT INTO polls (project_id, created_by, question, closes_at) VALUES (%s, %s, %s, %s)"
        poll_id = execute_query(poll_query, (project_id, user_id, question, closes_at), fetch_last_id=True)
        
        for option in options:
            option_query = "INSERT INTO poll_options (poll_id, option_text) VALUES (%s, %s)"
            execute_query(option_query, (poll_id, option))
        
        flash("Poll created successfully!", "success")
        return redirect(url_for('view_polls', project_id=project_id))
    
    return render_template('create_poll.html', project_id=project_id)

@app.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
def vote_poll(poll_id):
    user_id = session['user_id']

    team_query = "SELECT team_id FROM users WHERE user_id = %s"
    team_id = fetch_query(team_query, (user_id,))[0]['team_id']

    project_team_query = """
        SELECT p.team_id
        FROM polls po
        JOIN projects p ON po.project_id = p.project_id
        WHERE po.poll_id = %s
    """
    project_team_id = fetch_query(project_team_query, (poll_id,))[0]['team_id']

    if team_id != project_team_id:
        flash("You are not allowed to vote in this poll.", "danger")
        return redirect(url_for('poll_projects'))

    check_vote_query = "SELECT COUNT(*) AS vote_count FROM poll_votes WHERE poll_id = %s AND user_id = %s"
    existing_vote = fetch_query(check_vote_query, (poll_id, user_id))[0]['vote_count']

    if existing_vote > 0:
        flash("You have already voted in this poll.", "warning")
        return redirect(url_for('poll_results', poll_id=poll_id))

    if request.method == 'POST':
        option_id = request.form['option']

        vote_query = "INSERT INTO poll_votes (poll_id, user_id, option_id) VALUES (%s, %s, %s)"
        execute_query(vote_query, (poll_id, user_id, option_id))

        flash("Vote submitted successfully!", "success")
        return redirect(url_for('poll_projects', poll_id=poll_id))

    poll_query = "SELECT question FROM polls WHERE poll_id = %s"
    poll = fetch_query(poll_query, (poll_id,))[0]

    options_query = "SELECT option_id, option_text FROM poll_options WHERE poll_id = %s"
    options = fetch_query(options_query, (poll_id,))

    return render_template("vote_poll.html", poll=poll, options=options)

@app.route('/close/<int:poll_id>', methods=['POST'])
def close_poll(poll_id):
    user_id = session['user_id']

    creator_query = "SELECT created_by FROM polls WHERE poll_id = %s"
    poll_creator = fetch_query(creator_query, (poll_id,))[0]['created_by']

    if user_id != poll_creator:
        flash("Only the poll creator can close this poll.", "danger")
        return redirect(request.referrer)
    
    close_query = "UPDATE polls SET is_closed = TRUE WHERE poll_id = %s"
    execute_query(close_query, (poll_id,))
    
    flash("Poll closed successfully!", "success")
    return redirect(request.referrer)

@app.route('/results/<int:poll_id>')
def poll_results(poll_id):
    poll_query = "SELECT project_id, is_closed FROM polls WHERE poll_id = %s"
    poll_data = fetch_query(poll_query, (poll_id,))[0]
    
    if not poll_data['is_closed']:
        flash("Poll results will be available after the poll is closed.", "warning")
        return redirect(request.referrer)

    project_id = poll_data['project_id']

    poll_info_query = "SELECT question FROM polls WHERE poll_id = %s"
    poll_info = fetch_query(poll_info_query, (poll_id,))[0]

    options_query = """
        SELECT po.option_text, COUNT(pv.vote_id) AS votes
        FROM poll_options po
        LEFT JOIN poll_votes pv ON po.option_id = pv.option_id
        WHERE po.poll_id = %s
        GROUP BY po.option_text
    """
    options = fetch_query(options_query, (poll_id,))

    labels = [opt['option_text'] for opt in options]
    votes = [opt['votes'] for opt in options]

    fig = plt.figure(figsize=(8, 4))
    plt.barh(labels, votes, color='skyblue')
    plt.xlabel('Votes')
    plt.ylabel('Options')
    plt.title(poll_info['question'])

    chart_url = f"poll_result_{poll_id}.png"
    fig.savefig(f"static/{chart_url}", bbox_inches='tight')
    plt.close()

    return render_template('poll_results.html', poll_info=poll_info, chart_url=chart_url, project_id=project_id)

# ------------------------- Working Hours Management Routes -------------------------

@app.route('/working/<int:user_id>', methods=['GET', 'POST'])
def working(user_id):
    debug_logs = []
    user_id = session['user_id']
    if request.method == 'GET':
        return render_template('working.html', user_id=user_id)
    elif request.method == 'POST':
        date = request.form['date']
        hours = request.form['hours']
        try:
            execute_query("INSERT INTO working_hours (user_id, date, hours) VALUES (%s, %s, %s)", (user_id, date, hours))
            return redirect('/dashboard')
        except Exception as e:
            debug_logs.append(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
