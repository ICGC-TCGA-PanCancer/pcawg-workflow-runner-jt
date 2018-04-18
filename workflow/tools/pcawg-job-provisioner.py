#!/usr/bin/env python3

import os
import sys
import requests
import zipfile
from io import BytesIO
import json
import re
import subprocess

from utils import get_task_dict, save_output_json, get_input_path, get_output_path, get_reference_path

def parse_input_file(filename):
    fname = filename[filename.find("(") + 1:filename.find(")")]
    type = filename[filename.find("{") + 1:filename.find("}")]
    repo_code = None
    out_dir = filename[filename.find("[") + 1:filename.find("]")]
    url = None
    out_fname = fname.split(':')[-1]
    if fname.startswith('gnos://'):
        repo_code = fname.split('/')[2]
    elif fname.startswith('https://'):
        url = fname
    return {
        'source': fname.split('://')[0],
        'repo_code': repo_code,
        'type': type,
        'url': url,
        'out_file': out_dir,
        'fname_pattern': out_fname,
        'placeholder':filename
    }

def array_contains(fname, array_of_contains):
    for string_contain in array_of_contains:
        if string_contain not in fname:
            return False
    return True


def get_gnos_urls(fname_pattern, metadata_url):
    copies = []
    for hit in json.loads(requests.get(metadata_url).text).get('hits'):
        for file_copy in hit.get('fileCopies'):
            if array_contains(file_copy.get('fileName'), fname_pattern.split('*')):
                copies.append({'name':file_copy.get('fileName'),'url':file_copy.get('repoBaseUrl')+file_copy.get('repoDataPath')+file_copy.get("repoDataBundleId")})
    return copies

def walk_dict2(d, metadata_url, keys=[]):
    for key, value in d.items():
        if isinstance(value, dict):
            keys = walk_dict2(value, metadata_url, keys + [key])
        elif isinstance(value, list):
            for item in value:
                keys = walk_dict2({key:item}, metadata_url, keys + [key])
        else:
            pattern = re.compile("\{.*\}\[.*\](.*)")
            if pattern.match(str(value)):
                file_info = parse_input_file(value)
                if file_info.get('source') == 'gnos':
                    gnos_info = get_gnos_urls(file_info.get('fname_pattern'), metadata_url)
    return keys[:-1]

def download_https_file(url):
    r = requests.get(url, stream=True)
    with open('tmp', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def download_gnos_file(path_to_key,data_download_uri):
    subprocess.check_output(['gtdownload','-c',path_to_key, data_download_uri])


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
