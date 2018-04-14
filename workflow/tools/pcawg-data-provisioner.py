#!/usr/bin/env python3

import os
import sys
from utils import get_task_dict, save_output_json
from pcawg_workflow.utils import hyphen_to_camel_case
from pcawg_workflow.pcawg_cocleaning import PcawgCocleaning
from pcawg_workflow.pcawg_oxog_filter import PcawgOxogFilter
from pcawg_workflow.pcawg_snv_indel_annotation import PcawgSnvIndelAnnotation


task_dict = get_task_dict(sys.argv[1])
cwd = os.getcwd()

workflow_name = task_dict.get('input').get('workflow_name')
workflow_version = task_dict.get('input').get('workflow_version')
workflow_type = task_dict.get('input').get('workflow_type')
metadata = task_dict.get('input').get('metadata')
metadata_service = task_dict.get('input').get('metadata_service')
local_path = task_dict.get('input').get('local_path')
output = task_dict.get('input').get('output')
job_file_template = task_dict.get('job_file_template')

workflow_class_name = hyphen_to_camel_case(workflow_name)

provisioner_class = eval(workflow_class_name)
provisioner = provisioner_class(
                                workflow_version=workflow_version,
                                workflow_type=workflow_type,
                                metadata=metadata,
                                metadata_service=metadata_service,
                                local_path=local_path,
                                output=output,
                                job_file_template=job_file_template
                                )
provisioner.provision_files()

output_json = {
    'job_file': provisioner.job_file,
    'wf_file': provisioner.wf_file
}

save_output_json(output_json)
