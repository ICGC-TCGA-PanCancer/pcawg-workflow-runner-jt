import os
import sys
from utils import get_task_dict, save_output_json
import subprocess


task_dict = get_task_dict(sys.argv[1])
cwd = os.getcwd()

job_file = task_dict.get('job_file')
wf_file = task_dict.get('wf_file')

success = True  # assume task complete
stdout = ''
stderr = ''

p = subprocess.Popen(["cwltool --debug --non-strict --relax-path-checks %s %s" % (wf_file, job_file)],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
try:
    stdout, stderr = p.communicate()
except Exception as e:
    success = False  # task failed

if p.returncode != 0 or success is False:
    success = False
    with open('cwltool.stdout.txt', 'w') as o:
        o.write(stdout.decode("utf-8"))
    with open('cwltool.stderr.txt', 'w') as e:
        e.write(stderr.decode("utf-8"))
    sys.exit(1)

output_json = {
}

save_output_json(output_json)
