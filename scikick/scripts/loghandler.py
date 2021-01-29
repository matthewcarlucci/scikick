import sys

def log_handler(msg):
    # print(msg) # for development
    if msg['level'] == "job_error" and msg['name'] in \
    ['sk_exe_rmd','sk_exe_r','sk_exe_ipynb']:
        sys.stderr.write("sk: Error while generating " + msg['output'][0] + ". From " + msg['log'][0] + ':\n')
        f = open(msg['log'][0])
        for line in f:
            sys.stderr.write('sk:    ' + line)
        f.close()
        sys.stderr.write("sk: Error while generating " + msg['output'][0] + '\n')

