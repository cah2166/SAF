#!/usr/bin/python
import myModules, logging, os

#Program function
DESCRIPTION="My Forensic Program"
VERSION='1.7'


if __name__ == '__main__':
    #Calls multiple functions in the support module to generate logs and store in log_filename. 
    myModules.logModule.ParseCmdLine(DESCRIPTION)
    # Creates the log directory if it doesn't exist
    logdir=os.path.abspath('.')+'/'+myModules.logModule.gl_args.case
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    # Creates the case corpus directory if it doesn't exist    
    rootOfCorpus=os.path.expanduser('~')+'/nltk_data/corpora/casecorpus/'+myModules.logModule.gl_args.case
    if not os.path.exists(rootOfCorpus):
        os.makedirs(rootOfCorpus)

    # Gets prefix for logfile
    prefix=myModules.logModule.getPrefix()

    # Generates string based off of PREFIX argument and time generates in the support getTime function
    log_filename=''.join([prefix,myModules.logModule.getDate(),'.txt'])

    # Create basic syntax configuration for logging 
    logging.basicConfig(filename=logdir+'/'+log_filename, level=logging.DEBUG, format='%(asctime)s %(message)s')
    
    # Calls start log using global variables and checkExternalTime from support
    myModules.logModule.startLog(DESCRIPTION,VERSION)
    myModules.logModule.checkExternalTime()
    myModules.logModule.additionalLogs()
    # Gets into the scanning module of the program
    myModules.logModule.mainMod()

    # Called from maingprog to store done string in the log when main finishes to excute
    myModules.logModule.msg('done')