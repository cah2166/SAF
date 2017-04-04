import nltk.corpus, re, os, logModule, sys
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

def caseCorp():
    # Pulls all the cleaned files stored in the corpus directory from the log folder
    rootOfCorpus=os.path.expanduser('~')+'/nltk_data/corpora/casecorpus/'+logModule.gl_args.case+'/'
    newCorpus=PlaintextCorpusReader(rootOfCorpus,'.*')
    try:
        rawText=newCorpus.raw() # Creates raw text of corpus file
        tokens=nltk.word_tokenize(rawText) # Tokenizes the raw text
        logModule.msg('The Case Corpus Tokenized results: \n\n\n')
        textCase=nltk.Text(tokens) # stores text of tokenized values
    except:
        msg("Issue occured createing corpus.\n")
    if logModule.gl_args.keyWords and (logModule.gl_args.concord or logModule.gl_args.wordCount):
        # Block for comparing a keyword search against the corpus text using corpus word count and concordance
        fkey=open(logModule.gl_args.keyWords,'r') # opens keyword list file
        keylist=fkey.readlines() # stores keyword files into keylist
        fkey.close()
        for key in keylist: # loops through each keyword list item
            if logModule.gl_args.concord: # Enters block for computing concordance
                logModule.msg('\nKey search for '+key.strip()+' yields: ')
                # the following lines is a work around for taking the output of concordance and sotring it in a file
                saveout = sys.stdout # sets temporary system standard out tp saveout placeholder
                logfilename=logModule.gl_args.case+'/concord.log' # Path for temporary logfile is opened
                SavedConcordance = open(logfilename, 'w') # Opens temporary file
                sys.stdout = SavedConcordance # sets system standard out to the temporary file
                textCase.concordance(key.strip()) # Computes the output of concordance usually sent to stdout but instead sent to the SavedCondordance file
                sys.stdout=saveout # Restores the system standard output
                SavedConcordance.close() # Closes the temporary file
                with open(logfilename) as f: # opens the files from the stored output
                    lines = f.readlines() 
                    for line in lines:
                        logModule.msg(line.strip()) # sends the content of the corpus output to log and/or print to stdout
            if logModule.gl_args.wordCount: # Enters block for wordcount
                logModule.msg('\''+key.upper().strip()+'\' was found '+str(textCase.count(key.strip().upper()))+' times.') # The previous line uses the corpus tokenized text to count occurences of keyword item. It is case senitive and therefore updated to upper. This is why the corpus was cleaned to upper case in scanned.copyCorpus().

    if logModule.gl_args.dic: # Block once the corpus tokenized text is created and dictionary maker flag is on
        uniWords={} # Unique word set to store all corpus text
        uniqueCase=set(textCase)
        for item in uniqueCase: # for each item in the textCase corpus text set
            item=re.sub(r'[^\x00-\x7f]',r' ',item) # The text is cleaned for ascii hex text
            if len(item) < 3 or len(item) > 20: # focuses on building the list of text between 3 and 20 characters
                continue
            uniWords[str(item.encode("hex"))]=item # Adds the word to the dictionary with the hex value as the key
            logModule.msg('Item '+str(item)+' added to word hex dictionary') # Value is added to the log and stdout
        dfName=os.path.abspath('.')+'/'+logModule.gl_args.case+'/words' # Path for writing corpus word dictionary
        with open(dfName, "a") as f:
            for item in uniWords:
                f.write(item+':'+uniWords[item]+'\n') # writes the dictionary contents to a word file in the case folder