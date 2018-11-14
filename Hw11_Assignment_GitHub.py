import os
import sqlite3                                       
from prettytable import PrettyTable

#os.chdir('/Users//Desktop/PYFILES')          

def HW11_instructors(path):

    query = 'Select CWID, Name, Dept, Course, count(Course) as cnt from HW11_instructors left join HW11_grades on CWID=Instructor_CWID group by CWID, Name, Dept, Course'       

    connect = sqlite3.connect(path)                    
    pt = PrettyTable(field_names = ['CWID', 'Name', 'Dept', 'Course', 'Students'])
    
    for row in connect.execute(query):                 
        pt.add_row(row)

    print(pt)

HW11_instructors(r'C:\Users\Dell\Desktop\jini\810_database.db')