import sys
import os

def log_handler(msg):
    # print(msg) # for development
    if msg['level'] == "job_error" and msg['name'] in \
    ['sk_exe_rmd','sk_exe_r','sk_exe_ipynb']:
        logfile=msg['log'][0]
        sys.stderr.write("sk: Error while generating " + msg['output'][0] + ".  From " + logfile + ':\n')
        if not os.path.isfile(logfile):
            sys.stderr.write('sk:    Log file: ' + logfile + ' not found\n')
        else:
            f = open(logfile)
            for line in f:
                sys.stderr.write('sk:    ' + line)
            f.close()
            sys.stderr.write("sk: Error while generating " + msg['output'][0] + '\n')

