import unittest
import os
from collections import defaultdict
from prettytable import PrettyTable


def file_reader(path, num_fields, sep='\t', header=False):
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

    def __init__(self, wdir, ptables=True):
        self._wdir = wdir  # directory with students, instructor, grades files
        self._students = dict()  # key: cwid value: instance of class student
        self._instructors = dict()  # key: cwid value: instance of class instructor
        self._majors = dict()  # key : name of major value: instance of class major
        # self._grades = list() #a list of all grades

        self._get_majors(os.path.join(wdir, 'majors.txt'))  # read majors file
        # read student file
        self._get_students(os.path.join(wdir, 'students.txt'))
        # read instructor file
        self._get_instructors(os.path.join(wdir, 'instructors.txt'))
        self._get_grades(os.path.join(wdir, 'grades.txt'))  # read grade file

        if ptables:
            print('\n Major Summary')
            self.majors_table()

            print('\n Student Summary')
            self.student_table()

            print('\n Instructor Summary')
            self.instructor_table()

    def _get_majors(self, path):
        ''' read majors from path and add to self._majors'''
        try:
            for major, flag, course in file_reader(path, 3, sep='\t', header=False):
                if major not in self._majors:
                    self._majors[major] = Major(major)

                self._majors[major].add_course(flag, course)
        except ValueError as e:
            print(e)

    def _get_students(self, path):
        ''' read students from path and add to self._students'''
        try:
            for cwid, name, major in file_reader(path, 3, sep='\t', header=False):
                if cwid in self._students:
                    print(f' Warning: cwid {cwid} already read from the file')
                else:
                    self._students[cwid] = Student(
                        cwid, name, major, self._majors[major])
        except ValueError as e:
            print(e)

    def _get_instructors(self, path):
        ''' read instructors from path and add to self._instructors'''
        try:
            for cwid, name, dept in file_reader(path, 3, sep='\t', header=False):
                if cwid in self._instructors:
                    print(f' Warning: cwid {cwid} already read from the file')
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
            for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, sep='\t', header=False):
                if student_cwid in self._students:
                    # tell student abt new course and grade
                    self._students[student_cwid].add_course(course, grade)
                else:
                    print(
                        f' Warning: student cwid {student_cwid} is not known in the file')

                if instructor_cwid in self._instructors:
                    self._instructors[instructor_cwid].add_student(
                        course)  # tell student abt new course and grade
                else:
                    print(
                        f' Warning: instructor cwid {instructor_cwid} is not known in the file')
        except ValueError as e:
            print(e)

    def majors_table(self):
        ''' print a PrettyTable with a summary of all majors '''
        pt = PrettyTable(
            field_names=['Major', 'Required Courses', 'Electives'])
        for major in self._majors.values():
            pt.add_row(major.pt_row())

        # major_detail = [major.pt_row() for major in self._majors.values()]
        # print(f"major_detail: {major_detail}")

        print(pt)

    def student_table(self):
        ''' print a PrettyTable with a summary of all students '''
        pt = PrettyTable(field_names=Student.pt_lables)
        for student in self._students.values():
            pt.add_row(student.pt_row())

        # student_detail = [student.pt_row() for student in self._students.values()]
        # print(f"student_detail: {student_detail}")

        print(pt)

    def instructor_table(self):
        ''' print a PrettyTable with a summary of all instructors '''
        pt = PrettyTable(
            field_names=['CWID', 'Name', 'Dept', 'Course', 'Students'])
        for instructor in self._instructors.values():
            for row in instructor.pt_row():
                pt.add_row(row)

        # instructor_detail = [row for instructor in self._instructors.values() for row in instructor.pt_row()]
        # print(f"instructor_detail: {instructor_detail}")

        print(pt)


class Student:
    ''' Represents a single student '''
    pt_lables = ['CWID', 'Name', 'Major', 'Completed Courses',
                 'Remaining Required', 'Remaining Electives']

    def __init__(self, cwid, name, major, majors):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._majors = majors  # an instance of class major for any major
        self._courses = dict()  # key : courses value: str with grade

        self.lables = ['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Electives']

    def add_course(self, course, grade):
        ''' note that this student earned grade in courses '''
        self._courses[course] = grade

    def pt_row(self):
        ''' returns a list of values needed to add a row to student table '''
        completed_courses, remaining_required, remaining_electives = self._majors.grade_chk(
            self._courses)
        return [self._cwid, self._name, self._major, completed_courses, remaining_required, remaining_electives]


class Major:
    ''' Track of all info. about a major with required courses and electives '''
    pt_lables = ['Major', 'Required Courses', 'Electives']

    def __init__(self, dept, passing=None):
        self._dept = dept
        self._required = set()
        self._electives = set()

        if passing is None:
            self._passing_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
        else:
            self._passing_grades = passing

    def add_course(self, flag, course):
        ''' note another required course or elective '''
        if flag.upper() == 'E':
            self._electives.add(course)
        elif flag.upper() == 'R':
            self._required.add(course)
        else:
            raise ValueError(
                f'Flag {flag} is invalid for course {course} in majors.txt')

    def grade_chk(self, course):
        ''' Calc. completed_courses, remaining_required, remaining_electives from a dict[course] = Grade for a single student '''
        completed_courses = {
            course for course, grade in course.items() if grade in self._passing_grades}
        remaining_required = self._required - completed_courses

        if self._electives.intersection(completed_courses):
            remaining_electives = None
        else:
            remaining_electives = self._electives

        return completed_courses, remaining_required, remaining_electives

    def pt_row(self):
        ''' return a list of values to populate PT for this '''
        return [self._dept, self._required, self._electives]


class Instructor:
    ''' Represents an Instructor '''
    pt_labels = ['CWID', 'Name', 'Department', 'Course', 'Students']

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        # key : courses value: no. of students in the course
        self._courses = defaultdict(int)

    def add_student(self, course):
        self._courses[course] += 1

    def pt_row(self):
        for course, count in self._courses.items():
            yield [self._cwid, self._name, self._dept, course, count]


class Stevens_test(unittest.TestCase):
    def test_stevens(self):

        stevens = Repository(r'C:\Users\Dell\Desktop\jini', False)

        expect_majors = [['SFEN', {'SSW 564', 'SSW 540', 'SSW 555', 'SSW 567'},
                          {'CS 501', 'CS 545', 'CS 513'}],
                         ['SYEN', {'SYS 800', 'SYS 612', 'SYS 671'},
                          {'SSW 540', 'SSW 810', 'SSW 565'}]]

        expect_students = [['10103', 'Baldwin, C', 'SFEN', {'SSW 567', 'SSW 687', 'CS 501', 'SSW 564'},
                            {'SSW 555', 'SSW 540'}, None], ['10115', 'Wyatt, X', 'SFEN',
                            {'SSW 567', 'SSW 687', 'SSW 564', 'CS 545'}, {'SSW 555', 'SSW 540'}, None],
                           ['10172', 'Forbes, I', 'SFEN', {'SSW 567', 'SSW 555'}, {'SSW 564', 'SSW 540'},
                            {'CS 501', 'CS 513', 'CS 545'}], ['10175', 'Erickson, D', 'SFEN',
                            {'SSW 567', 'SSW 687', 'SSW 564'}, {'SSW 555', 'SSW 540'}, {'CS 501', 'CS 513', 'CS 545'}],
                           ['10183', 'Chapman, O', 'SFEN', {'SSW 689'}, {'SSW 567', 'SSW 555', 'SSW 564', 'SSW 540'},
                            {'CS 501', 'CS 513', 'CS 545'}], ['11399', 'Cordova, I', 'SYEN', {'SSW 540'},
                            {'SYS 612', 'SYS 671', 'SYS 800'}, None],
                           ['11461', 'Wright, U', 'SYEN', {'SYS 611', 'SYS 750', 'SYS 800'},
                            {'SYS 612', 'SYS 671'}, {'SSW 565', 'SSW 810', 'SSW 540'}],
                           ['11658', 'Kelly, P', 'SYEN', set(), {'SYS 612', 'SYS 671', 'SYS 800'},
                            {'SSW 565', 'SSW 810', 'SSW 540'}], ['11714', 'Morton, A', 'SYEN',
                            {'SYS 611', 'SYS 645'}, {'SYS 612', 'SYS 671', 'SYS 800'},
                            {'SSW 565', 'SSW 810', 'SSW 540'}],
                           ['11788', 'Fuller, E', 'SYEN', {'SSW 540'}, {'SYS 612', 'SYS 671', 'SYS 800'}, None]]

        expect_instructors = [['98765', 'Einstein, A', 'SFEN', 'SSW 567', 4],
                              ['98765', 'Einstein, A', 'SFEN', 'SSW 540', 3],
                              ['98764', 'Feynman, R', 'SFEN', 'SSW 564', 3],
                              ['98764', 'Feynman, R', 'SFEN', 'SSW 687', 3],
                              ['98764', 'Feynman, R', 'SFEN', 'CS 501', 1],
                              ['98764', 'Feynman, R', 'SFEN', 'CS 545', 1],
                              ['98763', 'Newton, I', 'SFEN', 'SSW 555', 1],
                              ['98763', 'Newton, I', 'SFEN', 'SSW 689', 1],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 800', 1],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 750', 1],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 611', 2],
                              ['98760', 'Darwin, C', 'SYEN', 'SYS 645', 1]]

        major = [m.pt_row() for m in stevens._majors.values()]
        self.assertEqual(major, expect_majors)

        students = [s.pt_row() for s in stevens._students.values()]
        self.assertEqual(students, expect_students)

        instructors = [row for instructor in stevens._instructors.values() for row in instructor.pt_row()]
        self.assertEqual(instructors, expect_instructors)


def main():
    
    wdir = r'C:\Users\Dell\Desktop\jini'
    unittest.main(exit=False, verbosity=2)
    stevens = Repository(wdir)


if __name__ == '__main__':
    main()
