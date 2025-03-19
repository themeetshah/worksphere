# WorkSphere

**WorkSphere** is a **Flask-based project management system** that helps organizations efficiently manage teams, tasks, budgets, expenses, polls, and employee performance. It features **role-based access control**, graphical reports, and a structured **task management system**.  

## 🎥 Demo  
- Preview the project [here](demo.mp4).

## 🚀 Features

- ###  Authentication & Access Control
  - **Login System** (Flask-based)
  - **Role-Based Access Control**  
    - **Owner**: Full access  
    - **Manager**: Manages teams under them  
    - **Team Leader**: Manages their own team  
    - **Team Member**: Limited access to assigned tasks  

- ###  Team & Employee Management
  - Create, assign, and manage **teams and employees**
  - Team details with **task performance and project tracking**
  - Employee profile with **assigned projects, tasks and working hours**

- ###  Task Management
  - **Task assignment based on roles** (Owner, Manager, Team Leader)
  - **Task status tracking** (Pending, Completed)
  - **File upload support** for task submission

- ###  Budget & Expense Tracking
  - Set **project budgets** and track **expenses**  
  - Categorized Expenses
  - **Expense Approval System** (Only Managers can approve)  
  - **Pie charts & detailed reports** for tracking  

- ###  Poll & Voting System
  - **Team-based voting** (Only members of a team, including the team leader, can vote)
  - **Poll closing & results viewing**  
  - **Matplotlib Graphs** for poll results  

- ###  Reports & Analytics
  - **Project Reports (PDF)** with:  
    - Budget details  
    - Team details  
    - Task performance  
    - Expenses & poll results  
    - **Matplotlib graphs** for performance tracking

- ###  Future Features
  - **Budget alerts** when exceeding limits *(Planned)*  
  - **Face recognition login** *(Planned)*  
  - **Task reminders & notifications** *(Planned)*  

## 📁 Project Structure

```
WorkSphere/  
│── static/ # all images  
    │── reports/ # report pdfs and graphs  
        │── graphs/ # graphs in reports  
│── templates/ # HTML templates  
│── database # Database utilities  
    │── db_connection.py  
│── main.py # Main Flask application  
│── team_management.py # team management utilities  
│── requirements.txt # requirements for the system  
│── README.md # Project documentation  
```

## 🛠️ Installation

### Prerequisites:
- Python 3.x  
- MySQL (XAMPP recommended)  
- Flask  

### Setup:

1. Clone the repository:  
   ```git clone https://github.com/themeetshah/worksphere.git```  
   ```cd worksphere```

2. Install dependencies:  
    ```pip install -r requirements.txt```
    
3. Configure MySQL Database:  
    ```Start XAMPP and create a database named worksphere```  
    ```Import the worksphere.sql file```

4. Run the application:  
    ```python main.py```

5. Open in browser:  
    ```http://localhost:5000```
    
## 📌 Technologies Used

- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Charts & Graphs**: Matplotlib

## 🤝 Contribute to WorkSphere  

Feel free to contribute to WorkSphere by creating [**pull requests**](https://github.com/themeetshah/worksphere/pulls) or [submitting issues](https://github.com/themeetshah/worksphere/issues).  

---

### 👨‍💻 Developed by [**Meet Shah**](https://github.com/themeetshah)
