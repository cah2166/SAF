import logModule, grp, hashlib, magic, csv, os, time, pwd, mmap

def getFileAttr(full_filename):
    # Creates magic buffer to append the content of the file to get the encoded type
    magic_buf = ""
    # Sets a hash container to store the contents to be hashed using getHashType function
    # Conditional also set a htype string to store hash type
    if logModule.gl_args.md5sum:
        hash=hashlib.md5()
        htype='MD5SUM'
    elif logModule.gl_args.sha512:
        hash=hashlib.sha512()
        htype='SHA512'         
    elif logModule.gl_args.sha384:
        hash=hashlib.sha384()
        htype='SHA384'           
    elif logModule.gl_args.sha224:
        hash=hashlib.sha224()
        htype='SHA224'
    else:
        hash=hashlib.sha256()
        htype='SHA256'
    try:
        # Checks if argument passed to the variable is of type file
        if os.path.islink(full_filename):
            return
        if os.path.isfile(full_filename):
            # Opens the file in read byte mode
            with open(full_filename, 'rb') as f:
                # try statement reads the content of the file using mmap for efficieny of reading in large files
                try:
                    mm = mmap.mmap(f.fileno(), 0 , access=mmap.ACCESS_READ)
                    # The content extracted from mmap is then stored in the hash container
                    hash.update(mm.read(mm.size()))
                except:
                    hashdigest = 'Error'
                # Hashes the content stored in the hash container.            
                hashdigest=hash.hexdigest()
                # Parses the contents of the stat function with the file as input, breaking it up into 10 variables
                (mode,ino,dev,nlink,uid,gid,size,atime,mtime,ctime)=os.stat(full_filename)
                # Converts the machine time outputs of the file to the local time of the current machine
                m_time=time.ctime(mtime) # last modified time
                a_time=time.ctime(atime) # last accessed time
                c_time=time.ctime(ctime)
                # Uses the uid and gui raw numbers and converts the values to the human readable string
                uidstr=pwd.getpwuid(uid).pw_name
                gidstr=grp.getgrgid(gid).gr_name
                stat_UID = '%s(%s)' % (str(uid), uidstr)
                stat_GID = '%s(%s)' % (str(gid), gidstr)
                # Converts
                stat_mode = oct(mode % 0o1000)
                # Gets the content of the file ato read in the encoded type
                with magic.Magic() as m:
                    magic_buf = m.id_filename(full_filename)
                
                # Outputs all the values into a nice tab delimited string
                attrOutput=[full_filename,htype,hashdigest,stat_mode,stat_UID,stat_GID,m_time,a_time,c_time,magic_buf]
                logModule.msg('\t'.join(str(attr) for attr in attrOutput))
                # Write all the details to the csv file
                with open(logModule.gl_args.case+'/File_Attributes_Hash.csv', 'ab') as f:
                    writer=csv.writer(f)
                    writer.writerow(attrOutput)
        else:
            # If the file was unable to open in the if condition
            logModule.msg('Failed to open file : %s ' % full_filename)
    except:
        logModule.msg('Failure to get file attributes of: ' + full_filename)