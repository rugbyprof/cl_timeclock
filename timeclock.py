#!/usr/bin/env python
import sqlite3
import argparse
import sys
import time

sqlite_file = '/Users/griffin/timeclock_db.sqlite'
project_table = 'projects'
entries_table = 'entries'

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()


def new_project(name,description):
    """
    Adds a new project to db.
    Params:
        name_desc
    Returns: 
        Bool success
    """
    maxid = max_id()+1
    sql = 'INSERT INTO "projects" VALUES (%d,"%s","%s")' % (int(maxid),name,description)
    c.execute(sql)
    conn.commit()

def max_id():
    """
    Gets max id from table.
    Params:
        None
    Returns: 
        Max id (int)
    """
    sql = 'SELECT max(id) FROM projects'
    c.execute(sql)
    maxid = c.fetchall()
    maxid = maxid[0][0]
    return maxid

def list_projects():
    """
    Dumps project table
    Params:
        None
    Returns: 
        List of projects
    """
    sql = 'SELECT * FROM projects' 
    c.execute(sql)
    all_rows = c.fetchall()
    print(all_rows)

def check_project_exists(project):
    """
    Checks to see of project name exists in db.
    Params:
        project (string): unique identifier for project
    Returns: 
        T/F (bool)
    """
    sql = 'SELECT * FROM "projects" WHERE lower(name) = "%s" ' % (project.lower())
    c.execute(sql)
    all_rows = c.fetchone()
    return len(all_rows) > 0

def get_project_id(p):
    """
    Returns a numeric id for a project
    Params:
        project (string): unique identifier for project
    Returns: 
        id (int)
    """
    sql = 'SELECT id FROM "projects" WHERE lower(name) = "%s" ' % (p.lower())
    c.execute(sql)
    all_rows = c.fetchone()
    return all_rows[0]

def clock_in(project,timestamp=None):
    """
    Clock into a project. Checks to see if user was clocked out of previous session.
    Params:
        project (string): unique identifier for project
        timestamp (int): optional timestamp to clock in with
    Returns:
        success message?
    """
    id = get_project_id(project)
    if timestamp is None:
        timestamp = int(time.time())
    print(timestamp)
    sql = 'SELECT * FROM entries WHERE pid = "%s" ORDER BY pid,id' % (id)
    c.execute(sql)
    rows = c.fetchall()

    # ghetto ?
    if rows[-1][3] == None:
        print("You never clocked out!")


def clock_out(project,timestamp=None):
    pid = get_project_id(project)
    if timestamp is None:
        timestamp = int(time.time())
    print(timestamp)
    sql = 'SELECT * FROM entries WHERE pid = "%s" ORDER BY pid,id' % (pid)
    c.execute(sql)
    rows = c.fetchall()
    if rows[-1][3] == None:
        id = rows[-1][1]
        sql = 'UPDATE entries SET out = "%d" WHERE pid = "%d" AND id = "%d"' % (int(timestamp),int(pid),int(id))
        print(sql)
        c.execute(sql)
        conn.commit()
  

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--new_project", nargs=2   ,help='project_name and description',metavar=('Project','description'))
parser.add_argument("-i", "--clock_in",    nargs='*' ,help='Clocking in. usage: -i short_name')
parser.add_argument("-o", "--clock_out",   nargs='*' ,help='Clocking out. usage: -o short_name')
parser.add_argument("-s", "--summary",                help='Summarizes all projects ',action='store_true')
args = parser.parse_args()
dargs = vars(args)

# find out if any arguments were entered
total = 0
for k,v in dargs.items():
    if v is not None:
        total += 1

# no arguments means print help
if total == 0:
    parser.print_help()

if args.clock_in:
    if type(args.clock_in) is list:
        project,time = args.clock_in
    else:
        project = args.clock_in
        time = None
    check_project_exists(project)
    clock_in(project,time)
elif args.clock_out:
    if type(args.clock_out) is list:
        project,time = args.clock_out
    else:
        project = args.clock_out
        time = None
    if check_project_exists(project):
        clock_out(project,time)
elif args.new_project:
    name,description = args.new_project
    new_project(name,description)
elif args.summary:
    list_projects()


conn.close()

