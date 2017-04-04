#!/usr/bin/python
import argparse, ntplib, time, sys, platform, logging, glob, os
import searchReg, search, scanner, corpus, re

# Get the logging argument form the main program running to use for storing in msg
log = logging.getLogger(__name__)

# MTP server address usesd to validate clock times
NTP_SERVER='utcnist.colorado.edu' #Colorado

def ParseCmdLine(DESCRIPTION="Missing Name"):
    #This function verifies where the user specifies the path to relatively run the application. 
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    # Because the p flag argument is required our code was unable to run the progress any further
    parser.add_argument('-C','--case',required=True,help='Directory location to store files.') 
    parser.add_argument('-P','--prefix',action='store',help='Log File Prefix.') 
    parser.add_argument('-U','--utc', action='store_true',help='Log with UTC time instead of local time.') 
    parser.add_argument('-s','--scan',action='store',nargs='+',help='Files and directories to get scanned.') 
    parser.add_argument('-u','--url', action='store_true',help='Web address/URL to search in scan.') 
    parser.add_argument('-e','--email', action='store_true',help='Email address to search in scan.') 
    parser.add_argument('-i','--ipaddress', action='store_true',help='IP address to search in scan.') 
    parser.add_argument('-p','--phone', action='store_true',help='Phone Number to search in scan.') 
    parser.add_argument('-f','--find',action='store',help='User specified string to search in scan.') 
    parser.add_argument('-q','--quiet',action='store_true',help='Disables screen output. Log output is stil stored.')
    parser.add_argument('-k', '--keyWords',type=ValidateFileRead,action='store', help="specify the file containing search words")
    parser.add_argument('-cs','--corp',action='store_true', help="Runs the concordance option on NLTK")
    parser.add_argument('-D','--dic',action='store_true', help="Creates dictionary of unique words in corpus.")
    parser.add_argument('-cn','--concord',action='store_true', help="Runs the concordance option on NLTK")
    parser.add_argument('-w','--wordCount',action='store_true', help="Runs the word count option on NLTK")
    parser.add_argument('-m', '--theMatrix',type=ValidateFileRead,action='store',help="specify the weighted matrix file")
    parser.add_argument('-W', '--walk',action='store_true',help="Expands the search to scan child directory files")
    parser.add_argument('-A', '--fattr',action='store_true',help="Outputs the file attributes of the files scanned")
    parser.add_argument('-S224','--sha224', action='store_true',help='Runs the sha224 algorithm on file(s).') 
    parser.add_argument('-S256','--sha256', action='store_true',help='Runs the sha256 algorithm on file(s).') 
    parser.add_argument('-S384','--sha384', action='store_true',help='Runs the sha384 algorithm on file(s).') 
    parser.add_argument('-S512','--sha512', action='store_true',help='Runs the sha512 algorithm on file(s).') 
    parser.add_argument('-MD5','--md5sum', action='store_true',help='Runs the MD5 algorithm on file(s).') 
    global gl_args
    gl_args = parser.parse_args()
    # The following conidtional statement checks: if the scan flag is enabled when the programis called, it must
    # specify a search type flag as well
    if gl_args.scan and not (gl_args.url or gl_args.email or gl_args.ipaddress or gl_args.phone or gl_args.find or gl_args.keyWords or gl_args.theMatrix or gl_args.fattr or gl_args.dic):
            parser.error("--scan requires --url, --email, --ipaddress, --find, --phone, --keyWords, --theMatrix, to be enabled.")
    return

def ValidateFileRead(theFile):
    # Validate theFile is a valid readable file
    if not os.path.exists(theFile):
        raise argparse.ArgumentTypeError('File does not exist')
    # Validate the path is readable
    if os.access(theFile, os.R_OK):
        return theFile
    else:
        raise argparse.ArgumentTypeError('File is not readable')

def getDate():
    # This function either grabs the gm or utc time depending if the -u or -utc flag was was enabled
    now = time.time()
    return time.strftime("%m-%d-%Y")

def getPrefix():
    # This function returns the log prefix if specified
    if gl_args.prefix is not None:
        prefix=gl_args.prefix+'-'
    else:
        prefix='log-'
    return prefix

def getTime():
    # This function either grabs the gm or utc time depending if the -u or -utc flag was was enabled
    now = time.time()
    if gl_args.utc:
        return time.strftime("%H.%M.%S%z", time.gmtime(int(now)))
    else:
        return time.strftime("%H.%M.%S%z", time.localtime(int(now)))

def mainMod():
    if gl_args.scan is not None:
        # Loops through distint arguments provided with the scan flag
        for scanItem in gl_args.scan:
            # Loops through all the wildcard possibilities from an argument provided by the user
            scanner.scanMain(scanItem)
            #for name in glob.glob(scanItem):
            #    # Grabs the full path of the file and passes it to scanner for furhter logic
            #    scanner.scanFiles(name)
        
    if gl_args.scan is None and gl_args.keyWords:
        # If scan flag was not enabled but user want to run a keyword search against previously scanned words
        msg("Running keyword list: "+gl_args.keyWords+' against previously scanned words\n')
        search.scanKeyWords(gl_args.keyWords,gl_args.case)
        
    if gl_args.concord or gl_args.wordCount or gl_args.dic:
        rootOfCorpus=os.path.expanduser('~')+'/nltk_data/corpora/casecorpus/'+gl_args.case
        if os.listdir(rootOfCorpus):
            # Adds the file to the case corpus for later uses with NLTK library in corpus.py
            corpus.caseCorp()
        else:
            msg("Cannot run concordance, wordCount, or dictionary option without scanning files into the case corpus")
            msg("Add files to the case corpus using the --scan with files names after and --corpus flag set")

def checkExternalTime():
    ''' 
    Grabs the time from an NTP server from the address in the global variable using the ntplib. Then it compares the value with the current time by calculating the differnece. While checking it stores logging information using the msg command into the log file created from startLog.
    '''
    ntp = ntplib.NTPClient()
    msg('Time Verification')
    msg('NTP Server: ' + NTP_SERVER)
    # Colorado server is taking to long March remove return later
    try:
        ntpResponse = ntp.request(NTP_SERVER)
        if(ntpResponse):
            now = time.time()
            diff = now - ntpResponse.tx_time
            delay = ntpResponse.delay
            msg('Time difference is secs '+str(diff)+' and Network delay is '+str(delay)+' secs')  
    except:
        msg('Time Verification Failed For '+ NTP_SERVER +'!')

def msg(msg):
    log.info(msg) # consider to comment out for testing
    # grabs msg argument and stores it in a log from the main program running
    if not gl_args.quiet:
        print(msg)
    return

def startLog(DESCRIPTION="Missing", VERSION="Missing"):
    # Writes out the first messages for the log file to start
    msg('---')
    msg('Starting '+DESCRIPTION+' V'+VERSION)
    msg('')
    log_uname = ' '.join(platform.uname())
    msg('System information: ' + log_uname)
    msg('')
    msg('Program started at: '+getTime())

def additionalLogs():
    # Outputs the arguments when the program was called
    msg('Arguments: '+ ' '.join(sys.argv))
    # Outputs python build information python version numver and date
    msg('Python build running: '+' '.join(platform.python_build()))    