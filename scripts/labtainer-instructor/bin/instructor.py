#!/usr/bin/env python

# Instructor.py
# Description: * Read instructorlab.json and extract a zip file
#                containing the student lab work
#              * Call script to grade the student lab work

import json
import os
import sys
import zipfile
import time
import glob
import Grader
import GoalsParser
import ResultParser

UBUNTUHOME="/home/ubuntu"
studentslablist = {}

def printresult(gradesfile, LabIDStudentName, grades):
    gradesfile.write("%s" % LabIDStudentName)
    for (each_key, each_value) in grades.iteritems():
        #print "Current key is ", each_key
        #print "Current value is ", each_value
        if each_key.startswith('_'):
            # Skip, i.e., do not print if it starts with '_'
            continue
        else:
            if each_value:
                gradestring = '%s=%s' % (each_key, "P")
            else:
                gradestring = '%s=%s' % (each_key, "F")
            gradesfile.write('%s ' % gradestring)
    gradesfile.write('\n')

# Usage: Instructor.py
# Arguments: None
def main():
    #print "Running Instructor.py"
    if len(sys.argv) != 1:
        sys.stderr.write("Usage: Instructor.py\n")
        return 1

    instructorjsonfname = '%s/.local/instr_config/%s' % (UBUNTUHOME, "instructorlab.json")
    instructorconfigjson = open(instructorjsonfname, "r")
    instructorconfig = json.load(instructorconfigjson)
    instructorconfigjson.close()

    # Output grades.txt
    gradesfilename = '%s/%s' % (UBUNTUHOME, "grades.txt")
    gradesfile = open(gradesfilename, "w")
    gradesfile.write("\n")
    StudentHomeDir = '/home/ubuntu'
    lab_name_dir = '/home/ubuntu/.local/.labname'
    if not os.path.isfile(lab_name_dir):
        print('ERROR: no file at %s, perhaps running instructor script on wrong containers?')
        exit(1)

    with open(lab_name_dir) as fh:
        LabIDName = fh.read().strip()
    InstructorName = instructorconfig['instructorname']
    InstructorHomeDir = instructorconfig['instructorhomedir']
    InstructorBaseDir = instructorconfig['instructorbasedir']
    GraderScript = instructorconfig['graderscript']

    student_list = {}
    zip_files = glob.glob(InstructorHomeDir+'/*.zip')
    for zfile in zip_files:
        ZipFileName = os.path.basename(zfile)
        #print('zipfile is %s' % ZipFileName)
        DestinationDirName = os.path.splitext(ZipFileName)[0]
        if '=' in DestinationDirName:
            # NOTE: New format has DestinationDirName as:
            #       e-mail+labname '=' containername
            # get email_labname and containername
            email_labname, containername = DestinationDirName.rsplit('=', 1)
            # Replace the '=' to '/'
            DestinationDirName = '%s/%s' % (email_labname, containername)
            #print email_labname
        else:
            # Old format - no containername
            sys.stderr.write("ERROR: Instructor.py old format (no containername) no longer supported!\n")
            return 1
        student_id = email_labname.rsplit('.', 1)[0]
        #print "student_id is %s" % student_id
        if email_labname not in student_list:
            student_list[email_labname] = []
        student_list[email_labname].append(containername) 
        #print('append container %s for student %s' % (containername, email_labname))
        OutputName = '%s%s' % (InstructorHomeDir, ZipFileName)
        LabDirName = '%s%s' % (InstructorHomeDir, email_labname)
        DestDirName = '%s%s' % (InstructorHomeDir, DestinationDirName)
        InstDirName = '%s%s' % (InstructorBaseDir, DestinationDirName)

        #print "Student Lab list : "
        #print studentslablist
        if email_labname not in studentslablist:
            labdirnamelist = '%s %s %s' % (student_id, LabDirName, LabIDName)
            #print "labdirname is (%s)" % labdirnamelist
            studentslablist[email_labname] = []
            studentslablist[email_labname].append(labdirnamelist)
        else:
            if labdirnamelist not in studentslablist[email_labname]:
                studentslablist[email_labname].append(labdirnamelist)

        #print "Current ZipFilename is %s" % ZipFileName
        #print "Current DestinationDirName is %s" % DestinationDirName
        #print "Current DestDirName is %s" % DestDirName
        #print "Current InstDirName is %s" % InstDirName

        if os.path.exists(DestDirName):
            #print "Removing %s" % DestDirName
            os.system('rm -rf %s' % DestDirName)

        zipoutput = zipfile.ZipFile(OutputName, "r")
        ''' retain dates of student files '''
        for zi in zipoutput.infolist():
            zipoutput.extract(zi, DestDirName)
            date_time = time.mktime(zi.date_time + (0, 0, -1))
            dest = os.path.join(DestDirName, zi.filename)
            os.utime(dest, (date_time, date_time))

        zipoutput.close()


    for email_labname in student_list:
        # GoalsParser is now tied per student - do this after unzipping file
        # Call GoalsParser script to parse 'goals'
        ''' note odd hack, labinstance seed is stored on container, so need to fine one, use first '''
        DestinationDirName = '%s/%s' % (email_labname, student_list[email_labname][0])
        DestDirName = '%s%s' % (InstructorHomeDir, DestinationDirName)
        GoalsParser.ParseGoals(DestDirName)

        # Call ResultParser script to parse students' result
        #command = 'ResultParser.py %s %s %s %s' % (LabDirName, containername, InstDirName, LabIDName)
        #print "About to do (%s)" % command
        #os.popen(command)
        ResultParser.ParseStdinStdout(LabDirName, student_list[email_labname], InstDirName, LabIDName)
        #ResultParser.ParseStdinStdout(LabDirName, containername, InstDirName, LabIDName)

    #print "Student Lab list : "
    #print studentslablist
    for studentslabname in studentslablist:
        #print studentslablist[studentslabname]
        for eachlistitem in studentslablist[studentslabname]:
            student_id, LabDirName, LabIDName = eachlistitem.split()
            # Call grader script 
            #command = '%s %s %s' % (GraderScript, LabDirName, LabIDName)
            #print "About to do (%s)" % command
            #grades = os.popen(command).read().splitlines()
            grades = Grader.ProcessStudentLab(LabDirName, LabIDName)
            #print "After ProcessStudentLab Instructor, grades is "
            #print grades
            LabIDStudentName = '%s : %s : ' % (LabIDName, student_id)
            printresult(gradesfile, LabIDStudentName, grades)

    gradesfile.write("\n")
    gradesfile.close()

    # Inform user where the 'grades.txt' are created
    print "Grades are stored in '%s'" % gradesfilename
    return 0

if __name__ == '__main__':
    sys.exit(main())

