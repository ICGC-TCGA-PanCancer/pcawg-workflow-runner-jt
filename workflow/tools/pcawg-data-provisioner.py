#!/usr/bin/env python

import os
import sys
from utils import get_task_dict, save_output_json, hyphen_to_camel_case
from pcawg_workflow import PcawgSnvIndelAnnotation
from pcawg_workflow import PcawgOxogFilter


task_dict = get_task_dict(sys.argv[1])
cwd = os.getcwd()

workflow_name = task_dict.get('input').get('workflow_name')
workflow_version = task_dict.get('input').get('workflow_version')
icgc_donor_id = task_dict.get('input').get('icgc_donor_id')
local_input_dir = task_dict.get('input').get('local_input_dir')

workflow_class_name = hyphen_to_camel_case(workflow_name)

provisioner_class = eval(workflow_class_name)
provisioner = provisioner_class(workflow_version, icgc_donor_id, local_input_dir)
provisioner.provision_files()

output_json = {
    'job_file': provisioner.job_file,
    'wf_file': provisioner.wf_file
}

save_output_json(output_json)
