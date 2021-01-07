## Write some rules to build a manubot manuscript after
# a scikick workflow

rule manubot:
    input:  
    output:
    conda: 'manubot_env.yml'
    shell: 'build/build.sh'


