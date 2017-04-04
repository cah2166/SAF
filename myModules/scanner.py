import ntpath, os, logModule, fattr, searchReg, search, threading, Queue, string, glob

#Threading
MAXTHREADS = 4 # sets the maximum number of threads to use
# workQueue = queue.Queue() #3.6
workQueue = Queue.Queue() #2.7 builds a standard queue for the threads to grab jobs from
Qmutex = threading.Lock() 

#Threading Object overwrites the un portion of the thread libary to dowork for each thread
class workerThread(threading.Thread):
    def __init__(self, TID): 
        threading.Thread.__init__(self)
        self.TID = TID
    def run(self): # overwrides the run function in thread class to do the jobs
        doWork(self.TID) # calls doWork for each thread when inialize and will continue to do doWork until queue is done

def copyCorpus(file): # methid for copying files to case corpus folder
    fpr=open(file,'r') # opens original file
    fname=ntpath.basename(file)
    corpusFile=(os.path.expanduser('~')+'/nltk_data/corpora/casecorpus/'+logModule.gl_args.case+'/'+fname)
    fpw=open(corpusFile,'w') # opens a clean version of the file into a case corpus
    printable = set(string.printable) # Readable characters to extract from scanned files to clean corpus folder
    for line in fpr:
        fpw.write(filter(lambda x: x in printable, line).upper()) # sets characters to upper case to keep consistency for word count later
    fpr.close() # closes original scanned file
    fpw.close() # closes clean corpus file
    
def walkFiles(dirName):
    # First for loop parses the output from os.walk function output from the input provided
    logModule.msg('\n---   ---   ---   ---   ---   ---   ---   ---\nWalking down directory '+dirName+'\n---   ---   ---   ---   ---   ---   ---   ---\n')
    for root, dirs, names in os.walk(dirName):  
        # Second for loop goes though all the output from the names list result from os.walk. All files from input
        for name in names:
            full_name = os.path.join(root,name)
            scanFiles(full_name) # A file is passed to scanFiles for logic chain

def scanFiles(itemName):  # main block for the search flags
    scanItem=os.path.abspath(itemName) # Gets the absolute block of the argument passed
    if os.path.isfile(scanItem):
        # Depending on the search flag element, the searchReg module is called to scan the file using 
        # a tailored regular expression designed to locate that type of element
        if logModule.gl_args.fattr: # Gets the file attributes for the scanned item input
            fattr.getFileAttr(scanItem)
        if logModule.gl_args.url: # Searches scanItem for web URLs
            logModule.msg("Searching url strings in "+scanItem)
            searchReg.urlSearch( scanItem)
        if logModule.gl_args.email: # Searches scanItem for email address
            logModule.msg("Searching email strings in "+scanItem)
            searchReg.emailSearch( scanItem)
        if logModule.gl_args.ipaddress: # Searches scanItem for ip addresses
            logModule.msg("Searching IP address numbers in "+scanItem)
            searchReg.ipSearch( scanItem)
        if logModule.gl_args.phone: # Searches scanItem for phone numbers
            logModule.msg("Searching phone numbers in "+scanItem)
            searchReg.pNumSearch( scanItem)
        if logModule.gl_args.find: # Searches scanItem for a specified string
            logModule.msg("Searching \'"+logModule.gl_args.find+"\' in "+scanItem)
            searchReg.scanFileReg( scanItem, logModule.gl_args.find)
        if logModule.gl_args.keyWords or logModule.gl_args.theMatrix: # Searches a keyword or matrix file with scanItem
            logModule.msg("Searching keyword list file or matrix in "+scanItem)
            search.SearchWords(scanItem,logModule.gl_args.case)
        if logModule.gl_args.corp: # Sends file to copyCorpus function to clean and copy the file to case corpus folder
            logModule.msg("The file has been added to case corpus for later scans: "+ scanItem)
            copyCorpus(scanItem)
    elif os.path.isdir(scanItem) and logModule.gl_args.walk: # Gets all child files if a directory is passed and walk flag is enabled
        walkFiles(scanItem)

def doWork(ProcessID):
    while True: # loop will continue until exit condition in line 53
        Qmutex.acquire() # queue is locked so the thread or core can work with it
        if not workQueue.empty(): # queue is not empyt it will repeatedly enter this section
            filename = workQueue.get() # gets the next obkect from the queue
            Qmutex.release() # unlocks the queue so other cores or threads can work with the queue
            scanFiles(filename) # runs the getFileAttr from last weeks lab with the filename popped from the queue
        else:
            Qmutex.release() # If there are no more jobs then the single thread or single core is done - queue is unlocked
            return

def scanMain(glob_queue):
    # if the file is a file it simply gets added to the queue   
    #Multiprocessing Version enables multiprocessing locking to avoid collision
    Qmutex.acquire()
    for file in glob.glob(glob_queue):
        workQueue.put(file)
    Qmutex.release()
    threads = [] #List of thread objects
    #Start threads
    for tcount in range(0, MAXTHREADS): # loops from 0 to maxthreads which currrently set to 4
        thread = workerThread(tcount) # creates the workerThread for each tcount up to 4
        thread.start() # starts the thread which will inact the run method and go through the queues in dowork
        threads.append(thread) #List of the thread objects
        #Wait for threads to stop
    for tcount in threads: # this look will continue to interate through the workerthreads
        tcount.join() # this will wait until all worker threads are done with the queue and each thread finishes their last job
