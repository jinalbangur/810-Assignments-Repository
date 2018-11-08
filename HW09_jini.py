import unittest
import os 
from collections import defaultdict
from prettytable import PrettyTable

def file_reader(path, num_fields, sep = '\t', header = False):
    try:
        path = open(path, 'r')
   
    except FileNotFoundError:
        print('File Not found here', path)

    else:
        with path:
            for line_num, line in enumerate(path, 1): 
                line = line.strip()
                elements = line.split(sep)

                if len(elements) == num_fields:

                    if header is True and line_num == 1:
                        continue
                    yield tuple(elements)

class Repository:
    ''' Store all information  abt student and instructor'''

    def __init__(self, wdir, ptables = True):
        self._wdir = wdir #directory with students, instructor, grades files
        self._students = dict() #key: cwid value: instance of class student
        self._instructors = dict() #key: cwid value: instance of class instructor
        #self._grades = list() #a list of all grades

        self._get_students(os.path.join(wdir, 'students.txt')) #read student file
        self._get_instructors(os.path.join(wdir, 'instructors.txt')) #read instructor file
        self._get_grades(os.path.join(wdir, 'grades.txt')) #read grade file

        if ptables:
            print ('\n Student Summary')
            self.student_table()

            print ('\n Instructor Summary')
            self.instructor_table()
    
    def _get_students(self, path):
        ''' read students from path and add to self.students'''
        try:
            for cwid, name, major in file_reader(path, 3, sep = '\t', header = False):
                if cwid in self._students:
                    print (f' Warning: cwid {cwid} already read from the file')
                else:
                    self._students[cwid] = Student(cwid, name, major)
        except ValueError as e:
            print(e)

    def _get_instructors(self, path):
        ''' read instructors from path and add to self.instructors'''
        try:
            for cwid, name, dept in file_reader(path, 3, sep = '\t', header = False):
                if cwid in self._instructors:
                    print (f' Warning: cwid {cwid} already read from the file')
                else:
                    self._instructors[cwid] = Instructor(cwid, name, dept)
        except ValueError as e:
            print(e)

    def _get_grades(self, path):
        ''' read grades file with student_cwid, course, grade, instructor_cwid 
            inform student abt course and grade
            inform instructor abt new course and student
        '''
        try:
            for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, sep = '\t', header = False):
                if student_cwid in self._students:
                    self._students[student_cwid].add_course(course, grade) #tell student abt new course and grade
                else:
                    print (f' Warning: student cwid {student_cwid} is not known in the file') 
            

                if instructor_cwid in self._instructors:
                    self._instructors[instructor_cwid].add_student(course) #tell student abt new course and grade
                else:
                    print (f' Warning: instructor cwid {instructor_cwid} is not known in the file') 
        except ValueError as e:
            print (e) 
        
    def student_table(self):
        ''' print a PrettyTable with a summary of all students '''
        pt = PrettyTable(field_names = ['CWID', 'Name', 'Major', 'Completed Courses'])
        for student in self._students.values():
            pt.add_row(student.pt_row())

        print(pt)
    
    def instructor_table(self):
        ''' print a PrettyTable with a summary of all instructors '''
        pt = PrettyTable(field_names = ['CWID', 'Name', 'Dept', 'Course', 'Students'])
        for instructor in self._instructors.values():
            for row in instructor.pt_row():
                pt.add_row(row)

        print(pt)



class Student:
    ''' Represents a single student '''
    pt_lables = ['CWID', 'Name', 'Completed Courses']

    def __init__(self, cwid, name, major):
        self._cwid = cwid
        self._name = name
        self._major = major

        self._courses = dict() #key : courses value: str with grade
        self.lables = ['CWID', 'Name', 'Major', 'Courses']

    def add_course(self, course, grade):
        ''' note that this student earned grade in courses '''
        self._courses[course] = grade
    
    def pt_row(self):
        ''' returns a list of values needed to add a row to student table '''
        return [self._cwid, self._name, self._major, sorted(self._courses.keys())]
    
    def __str__(self):
        return f'Student: {self._cwid} name: {self._name} major: {self._major} courses: {sorted(self._courses.keys())}'



class Instructor:
    ''' Represents an Instructor '''
    pt_labels = ['CWID', 'Name', 'Department', 'Course', 'Students']
    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        self._courses = defaultdict(int) #key : courses value: no. of students in the course

    def add_student(self, course):
        self._courses[course] += 1

    def pt_row(self):
        for course, count in self._courses.items():
            yield [self._cwid, self._name, self._dept, course, count]

    def __str__(self):
        return f'Student: {self._cwid} name: {self._name} dept: {self._dept} courses: {sorted(self._courses.keys())}'



class Student_Test(unittest.TestCase):
    def test_student_test(self):

        stevens  = Repository(r'C:\Users\Dell\Desktop\jini')

        student_details = stevens._students['11788']
        expect = ('11788, Fuller, E, SYEN, [SSW 540]')

        print (student_details)
        
        
def main():
    wdir = r'C:\Users\Dell\Desktop\jini'
    stevens = Repository(wdir)
    
if __name__ == '__main__':
    main()
    unittest.main(exit=False, verbosity=2)





    