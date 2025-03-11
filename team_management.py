from database.db_connection import fetch_query, execute_query, get_user_role

def user_exists(user_id):
    """Checks if a user exists in the database."""
    query = "SELECT COUNT(*) as count FROM users WHERE user_id = %s"
    result = fetch_query(query, (user_id,))
    return result[0]['count'] > 0

def user_exists_email(email):
    """Checks if a user exists in the database."""
    query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
    result = fetch_query(query, (email,))
    return result[0]['count'] > 0

def team_exists(team_id):
    """Checks if a team exists in the database."""
    query = "SELECT COUNT(*) as count FROM teams WHERE team_id = %s"
    result = fetch_query(query, (team_id,))
    return result[0]['count'] > 0

def get_user_team(user_id):
    """Returns the team ID of the user if they are in a team, otherwise None."""
    query = "SELECT team_id FROM users WHERE user_id = %s"
    result = fetch_query(query, (user_id,))
    return result[0]['team_id'] if result and result[0]['team_id'] else None

def create_team(name, manager_id, creator_id):
    """Creates a team if the creator is an Owner or Manager and the manager is valid."""
    debug_logs = []
    role = get_user_role(creator_id)

    if role not in ["Owner", "Manager"]:
        print("❌ You don't have permission to create a team.")
        debug_logs.append("❌ You don't have permission to create a team.")
        return False, debug_logs
    
    if not user_exists(manager_id):
        print("❌ No such user with the given Manager ID.")
        debug_logs.append("❌ No such user with the given Manager ID.")
        return False, debug_logs

    if get_user_role(manager_id) != "Manager":
        print("❌ The entered ID does not belong to a Manager.")
        debug_logs.append("❌ The entered ID does not belong to a Manager.")
        return False, debug_logs

    query = "INSERT INTO teams (name, manager_id) VALUES (%s, %s)"
    execute_query(query, (name, manager_id))
    print("✅ Team created successfully!")
    debug_logs.append("✅ Team created successfully!")
    return True, debug_logs

def get_team_details(team_id, viewer_id):
    """Fetches team details including manager name and team leader name, ensuring access control."""
    debug_logs = []
    role = get_user_role(viewer_id)
    
    if role in ["Owner", "Manager", "Team Leader", "Team Member"]:
        # Owner can view any team
        query = """
            SELECT user_id, name, email, role FROM users WHERE team_id = %s;
        """
        return fetch_query(query, (team_id,))
    
    else:
        print("❌ You don't have permission to view team details.")
        debug_logs.append("❌ You don't have permission to view team details.")
        return ["Can't"], debug_logs

def get_all_teams(viewer_id):
    """Fetches teams based on the viewer's role."""
    debug_logs = []
    role = get_user_role(viewer_id)

    if role == "Owner":
        query = " SELECT t.team_id, t.name AS team_name, m.name AS manager_name, l.name AS leader_name FROM teams t JOIN users m ON t.manager_id = m.user_id LEFT JOIN users l ON t.leader_id = l.user_id;"
        teams = fetch_query(query)
        for team in teams:
            team['leader_name'] = team['leader_name'] if team['leader_name'] is not None else "Not Assigned"
        return teams

    elif role == "Manager":
        query = "SELECT t.team_id, t.name AS team_name, m.name AS manager_name, l.name AS leader_name FROM teams t JOIN users m ON t.manager_id = m.user_id LEFT JOIN users l ON t.leader_id = l.user_id WHERE manager_id = %s"
        teams = fetch_query(query, (viewer_id,))
        for team in teams:
            team['leader_name'] = team['leader_name'] if team['leader_name'] is not None else "Not Assigned"
        return teams

    elif role == "Team Leader":
        query = "SELECT t.team_id, t.name AS team_name, m.name AS manager_name, l.name AS leader_name FROM teams t JOIN users m ON t.manager_id = m.user_id JOIN users l ON t.leader_id = l.user_id WHERE leader_id = %s"
        return fetch_query(query, (viewer_id,))

    elif role == "Team Member":
        print("Team Member",viewer_id)
        query = "SELECT t.team_id, t.name AS team_name, m.name AS manager_name, l.name AS leader_name FROM teams t JOIN users m ON t.manager_id = m.user_id LEFT JOIN users l ON t.leader_id = l.user_id WHERE t.team_id = (Select team_id from users where user_id = %s)"
        teams = fetch_query(query, (viewer_id,))
        for team in teams:
            team['leader_name'] = team['leader_name'] if team['leader_name'] is not None else "Not Assigned"
        print(teams)
        return teams

    else:
        print("❌ You don't have permission to view all teams.")
        debug_logs.append("❌ You don't have permission to view all teams.")
        return [],debug_logs

def remove_user_from_team(user_id, team_id):
    """Removes a user from their current team if remover is Owner or Manager."""
    debug_logs = []
    role_remove = get_user_role(user_id)

    current_team = get_user_team(user_id)
    if not current_team:
        debug_logs.append("❌ This user is not in any team.")
        return False, debug_logs

    if role_remove != 'Team Leader':
        pending_task = fetch_query("SELECT COUNT(*) from tasks where status!='COMPLETE' and assigned_to=%s",(user_id,))
        if pending_task[0]['COUNT(*)'] > 0:
            debug_logs.append("❌ User has pending tasks and cannot be removed from the team.")
            return False, debug_logs
        else:
            query = "UPDATE users SET team_id = NULL, role='Employee' WHERE user_id = %s and team_id=%s"
            execute_query(query, (user_id,team_id))
            debug_logs.append(f"✅ User {user_id} removed from Team {current_team}.")
            return True, debug_logs
    else:
        debug_logs.append("❌ You can't remove a team leader from a team.")
        return False, debug_logs

def assign_user_to_team(user_id, team_id, role):
    """Assigns a user to a team with a specific role if assigner is Owner or Manager."""
    debug_logs = []

    if not user_exists(user_id):
        debug_logs.append("❌ No such user with the given User ID.")
        return False, debug_logs
    
    if not team_exists(team_id):
        debug_logs.append("❌ No such team with the given Team ID.")
        return False, debug_logs
    
    user_current_role = get_user_role(user_id)
    if user_current_role == "Manager":
        debug_logs.append("❌ A Manager cannot be assigned to a team.")
        return False, debug_logs
    
    if user_current_role == "Owner":
        debug_logs.append("❌ Owner cannot be assigned to a team.")
        return False, debug_logs

    if role not in ["Team Leader", "Team Member"]:
        debug_logs.append("❌ Invalid role. Only 'Team Leader' or 'Team Member' allowed.")
        return False, debug_logs
        
    member_team = get_user_team(user_id)
    member_role = get_user_role(user_id)
    if member_team is not None and member_team!=team_id:
        debug_logs.append(f"❌ User {user_id} already in Team {member_team} as {member_role}.")
        return False, debug_logs
        
    if role=="Team Leader":
        # check if leader already there
        query = "SELECT COUNT(*) FROM users WHERE team_id = %s AND role='Team Leader'"
        result = fetch_query(query, (team_id,))
        # print(result)
        if result[0]['COUNT(*)']:
            debug_logs.append(f"❌ Team {team_id} already has a Team Leader.")
            return False, debug_logs
                
    query = "UPDATE users set role=%s, team_id=%s where user_id=%s"
    execute_query(query, (role, team_id, user_id))
    if role=="Team Leader":
        query = "UPDATE teams set leader_id=%s where team_id=%s"
        execute_query(query, (user_id, team_id))
    debug_logs.append(f"✅ User {user_id} assigned to Team {team_id} as {role}.")
    return True, debug_logs
