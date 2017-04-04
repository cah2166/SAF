#!/usr/bin/python
import re
import mmap
import logModule
import docx
import PyPDF2

''' Following sections set up particular regular expressions for specific fields. They then pass the file and the regular expression to the scanFileReg that performs the searching based off the regex criteria'''

# Sets pattern a web address structure. Sometimes pulls email suffixes and number tuples as well because of similarities
def urlSearch(fName):
    cpattern=re.compile('(http\:\/\/|https\:\/\/)([a-z0-9][a-z0-9\-]*\.)+[a-z0-9][a-z0-9\-]+')
    scanFileReg(fName, cpattern)

# Sets pattern an email structure.
def emailSearch(fName):
    cpattern=re.compile('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
    scanFileReg(fName, cpattern)

# Sets pattern an IP address structure.
def ipSearch(fName):
    cpattern=re.compile('(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])')
    scanFileReg(fName, cpattern)
 
 # Sets pattern phone number structure.
def pNumSearch(fName):
    cpattern=re.compile('\+?[0-9]?[-.]?\(?[0-9][0-9][0-9]\)?[-.]?[0-9][0-9][0-9][-.][0-9][0-9][0-9][0-9]')
    scanFileReg(fName, cpattern)

# Scans the file based off the regular expression pattern provided
def scanFileReg(filename, pattern):
    # Checks if the file has an extension of docx - to improve considering to use a magic number check on the file
    if '.docx' in filename:
        try:
            # Uses docx library functions to extract data
            worddoc=docx.Document(filename)
            # Searches extracted data and compares the regular expression. If found writes it to the log file
            for para in worddoc.paragraphs:
                for matches in pattern.findall(para.text):
                    matchString=[s.encode('utf8') for s in matches]
                    logModule.msg("\t"+str(matchString))
        except:
            # If the extraction and comparison fail below exception specifies the whic file cause the error
            logModule.msg("\n*** Issue when attempting to scan the file in scanFileRef -- docx clause with file:\n"+"***"+filename)
    # Catches all other types of file and attempts to scan the files as clear text
    else:
        try:
            f=open(filename,'r')  
            # mmap can be used to break the file into chuncks to read portions to not overload the memory
            m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
            # Continues to go through the data until the end of the file
            while True:
                line = m.readline()  
                if line == "": break
                # Searches extracted data and compares the regular expression. If found writes it to the log file
                for matches in pattern.findall(line):
                    logModule.msg("Search string for "+"\t"+str(matches))
            m.close()
            f.close()
        except:
            # If the extraction and comparison fail below exception specifies the whic file cause the error
            logModule.msg("\n*** Issue when attempting to scan the file in scanFileRef -- else clause with file:\n"+"***"+filename)