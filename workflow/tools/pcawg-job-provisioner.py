#!/usr/bin/env python3

import json
import re
import sys
import zipfile
from io import BytesIO

from operations import *
from utils import get_task_dict, save_output_json, get_input_path, get_reference_path


task_dict = get_task_dict(sys.argv[1])
cwd = os.getcwd()

workflow = task_dict.get('input').get('workflow')
metadata = task_dict.get('input').get('metadata')
metadata_service = task_dict.get('input').get('metadata_service')
job_file_template = task_dict.get('input').get('job_file_template')


## TODO: start from job_file_template, download necessary input (and reference) data and populate
## job JSON fields with concrete values
input_path = get_input_path(metadata.get('pipeline'), metadata.get('job_partiption_key'), workflow.get('name'), workflow.get('version'))
reference_path = get_reference_path(metadata.get('pipeline'), metadata.get('job_partiption_key'), workflow.get('name'), workflow.get('version'))


# write out job JSON
job_file = 'job.json'


git_download_url = "%s/archive/%s.zip" % (workflow.get('repo_url'), workflow.get('version'))
request = requests.get(git_download_url)
zfile = zipfile.ZipFile(BytesIO(request.content))
zfile.extractall(os.getcwd())




def parse_placeholder(placeholder):
    _dict = {}
    _dict['output_dir'] = placeholder[1]
    _dict['output_type'] = placeholder[0]
    _dict['url'] = ':'.join(placeholder[2].split(":")[:-1])
    _dict['file_patterns'] = placeholder[2].split(':')[-1].split(',')
    _dict['source'] = placeholder[2].split(':')[0]
    _dict['placeholder'] = "{%s}[%s](%s)" % (placeholder[0], placeholder[1],placeholder[2])
    return _dict

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

def convert_patterns(_file_info, metadata_url):
    files = []
    for pattern in _file_info.get('file_patterns'):
        if _file_info.get('url').startswith('gnos'):
            _file_info['url'] = get_gnos_urls(pattern,metadata_url)[0].get('url')
    return _file_info


job_dict = json.loads(sys.argv[1])
size = str(job_dict.get('metadata_service').get('params').get('size'))
filters = json.dumps(job_dict.get('metadata_service').get('params').get('filters'))
metadata_url = str(
    job_dict.get('metadata_service').get('url') + "?filters=" + filters.replace(' ', '') + "&size=" + size)

with open('annotation_test.json', 'r') as _f:
    data = _f.read()

_to_replace = []

for _match in re.findall(r"\{\{.*\}\}", data):
    _to_replace.append({'placeholder': _match, 'value': 'tmp'})

for l in _to_replace:
    data = data.replace(l.get('placeholder'), l.get('value'))

for _match in list(set(re.findall(r"\{(.+?)\}\[(.+?)\]\((.+?)\)", data))):
    _match_data = parse_placeholder(_match)
    _match_data = convert_patterns(_match_data, metadata_url)

    if _match_data.get('url').endswith('.tar.gz'):
        value = pipeline_download_decompress_mv(_match_data.get('url'), _match_data.get('source'),
                                                _match_data.get('file_patterns'), _match_data.get('output_dir'),
                                                _match_data.get('output_type'))
    elif _match_data.get('source') == "file":
        value = pipeline_nothing(_match_data.get('url'), _match_data.get('source'), _match_data.get('file_patterns'),
                                 _match_data.get('output_type'))
    else:
        value = pipeline_download_mv(_match_data.get('url'), _match_data.get('source'),
                                     _match_data.get('file_patterns'), _match_data.get('output_dir'),
                                     _match_data.get('output_type'))

    _to_replace.append({'placeholder': _match_data.get('placeholder'), 'value': value})

for l in _to_replace:
    data = data.replace(l.get('placeholder'),l.get('value'))

with open(job_file, 'w') as outfile:
    json.dump(data,outfile)




output_json = {
    'job_file': job_file,
    'wf_file': os.path.join(os.getcwd(), "%s-%s" % (workflow.get('name'), workflow.get('version')), workflow.get('workflowfile_name'))
}

save_output_json(output_json)
