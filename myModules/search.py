import os, logModule, pickle, sys, ntpath

#Constants 
MIN_WORD = 5                     # Minimum word size in bytes
MAX_WORD = 15                      # Maximum word size in bytes
PREDECESSOR_SIZE = 32           # Values to print before match found
WINDOW_SIZE = 128                # Total values to dump when match found

def SearchWords(srchTarget,caseNum):    
    # Attempt to open and read the target file
    # and directly load into a bytearray
    try:
        targetFile = open(srchTarget, 'rb')
        baTarget = bytearray(targetFile.read())
    except:
        logModule.msg('Target File Failure: ' + srchTarget)
        sys.exit()
    finally:
        targetFile.close()

    sizeOfTarget= len(baTarget)

    # Post to log    
    logModule.msg('Target of Search: ' + srchTarget)
    logModule.msg('File Size: '+str(sizeOfTarget))
    baTargetCopy = baTarget    

    # Create an empty set of search words
    searchWords = set()
    # Attempt to open and read search words
    if (logModule.gl_args.keyWords):    
        keyWords= logModule.gl_args.keyWords
        try:
            fileWords = open(keyWords)
            for line in fileWords:
                upline=line.upper()
                searchWords.add(upline.strip())
        except:
            logModule.msg('Keyword File Failure: ' + keyWords)
            sys.exit()   
        finally:
            fileWords.close()
        # Create Log Entry Words to Search For
        logModule.msg('Search Words')
        logModule.msg('Input File: '+keyWords)
        logModule.msg(searchWords)

    if (logModule.gl_args.theMatrix):
        wordCheck = class_Matrix()

    # Search Loop
    # step one, replace all non characters with zero's
    for i in range(0, sizeOfTarget):
        character = chr(baTarget[i])
        if not character.isalpha():
            baTarget[i] = 0
    
    # step # 2 extract possible words from the bytearray
    # and then inspect the search word list
    # create an empty list of probable wnot found items
    
    indexOfWords = []

    cnt = 0
    for i in range(0, sizeOfTarget):
        character = chr(baTarget[i])
        if character.isalpha():
            cnt += 1
        else:
            if (cnt >= MIN_WORD and cnt <= MAX_WORD):
                newWord = ""
                for z in range(i-cnt, i):
                    newWord = newWord + chr(baTarget[z])
                newWord = newWord.upper()
                if (logModule.gl_args.keyWords):
                    if (newWord in searchWords):
                        indexOfWords.append([newWord, i-cnt])
                    cnt = 0
                if (logModule.gl_args.theMatrix):
                    if wordCheck.isWordProbable(newWord):
                        indexOfWords.append([newWord, i-cnt])
                    cnt = 0    
            else:        
                cnt = 0
                
    logModule.msg("\n\nIndex of All Words")
    indexOfWords.sort()
    
    bfName=ntpath.basename(srchTarget)
    csvFile=open(caseNum+'/output.csv', 'a')
    index=[]
    for entry in indexOfWords:
        hexStr=str(entry[0].encode("hex"))
        logModule.msg(str(entry[0])+','+str(entry[1])+','+hexStr+','+bfName)
        index.append([entry[0],entry[1],bfName])
        csvFile.write(str(entry[0])+','+str(entry[1])+','+bfName+'\n')
    csvFile.close()
    
    if os.path.exists(caseNum+'/indexWords'):
        with open(caseNum+'/indexWords','rb') as rpdb: 
            casedb = pickle.load(rpdb)
        casedb.append(index)
        with open(caseNum+'/indexWords','wb') as wpdb:
            pickle.dump(casedb, wpdb)        
    else:
        with open(caseNum+'/indexWords','wb') as wpdb:
            pickle.dump(index, wpdb)          

    return


def scanKeyWords(keyWords,caseNum):
    try:
        items=pickle.load(open(caseNum+'/indexWords','rb'))
    except:
        logModule.msg('Failure to open Pickle File')
        sys.exit()

    f=open(keyWords,'r')
    for line in f:
        line=line.strip().upper()
        for item in items:
            word=str(item[0]).strip().upper()
            if (word==line):
                logModule.msg('Word '+word+' was found at offset '+str(item[1])+' in file '+str(item[2]))
    f.close()    


# Class Matrix
# init method, loads the matrix into the set
# weightedMatrix
# isWordProbable method
#   1) Calcuates the weight of the provided word
#   2) Verifies the minimum length
#   3) Calculates the weight for the word
#   4) Tests the word for exsistance in the matrix
#   5) Returns true or fales
class class_Matrix:
    weightedMatrix = set()
    def __init__(self):
        try:
            matrix=os.path.abspath(logModule.gl_args.theMatrix)
            fileTheMatrix = open(matrix, 'rb')
            for line in fileTheMatrix:
                    value = line.strip()
                    self.weightedMatrix.add(int(value,16))
        except:
            logModule.msg('Matrix File Error: ' + theMatrix)
            sys.exit()
        finally:
            fileTheMatrix.close()        
        return

    def isWordProbable(self, theWord): 
        if (len(theWord)<MIN_WORD):
            return False
        else:
            BASE = 64
            wordWeight = 0
            for i in range(4,0,-1):
                charValue = (ord(theWord[i])-BASE)
                shiftValue = (i-1)*8
                charWeight = charValue << shiftValue
                wordWeight = (wordWeight | charWeight)        

            if ( wordWeight in self.weightedMatrix):
                    return True
            else:
                    return False

