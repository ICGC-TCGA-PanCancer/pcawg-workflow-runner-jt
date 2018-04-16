#!/usr/bin/env python3

import os
import sys
import requests
import zipfile
from io import BytesIO

from utils import get_task_dict, save_output_json, get_input_path, get_output_path, get_reference_path


task_dict = get_task_dict(sys.argv[1])
cwd = os.getcwd()

workflow_name = task_dict.get('input').get('workflow').get('name')
workflow_version = task_dict.get('input').get('workflow').get('version')
workflowfile_name = task_dict.get('input').get('workflow').get('workflowfile_name')
workflow_type = task_dict.get('input').get('workflow').get('type')
repo_url = task_dict.get('input').get('workflow').get('repo_url')
pipeline = task_dict.get('input').get('metadata').get('pipeline')
job_partiption_key = task_dict.get('input').get('metadata').get('job_partiption_key')
metadata_service = task_dict.get('input').get('metadata_service')
job_file_template = task_dict.get('input').get('job_file_template')


## TODO: start from job_file_template, download necessary input (and reference) data and populate
## job JSON fields with concrete values
input_path = get_input_path(pipeline, job_partiption_key, workflow_name, workflow_version)
reference_path = get_reference_path(pipeline, job_partiption_key, workflow_name, workflow_version)


# write out job JSON
job_file = 'job.json'


git_download_url = "%s/archive/%s.zip" % (repo_url, workflow_version)
request = requests.get(git_download_url)
zfile = zipfile.ZipFile(BytesIO(request.content))
zfile.extractall(os.getcwd())


output_json = {
    'job_file': job_file,
    'wf_file': os.path.join(os.getcwd(), "%s-%s" % (workflow_name, workflow_version), workflowfile_name)
}

save_output_json(output_json)
