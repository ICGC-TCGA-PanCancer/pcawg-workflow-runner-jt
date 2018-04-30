import os
import json


def get_task_dict(json_string):
    try:
        task_dict = json.loads(json_string)
    except:
        return {}

    return task_dict


def save_output_json(output_dict={}):
    with open('output.json', 'w') as f:
        f.write(json.dumps(output_dict, indent=2))


def get_workdir():
    return os.getcwd()


def get_workflow_path(pipeline, job_partiption_key, workflow_name, workflow_version):
    """
    jthome
    ├── account.2eea3942-2c9c-4cdb-ad6f-606d062730e5
    └── data
        └── pipeline.PCAWG  # pipeline
            └── DO36881  # job_partiption_key
                └── pcawg-oxog-filter  # workflow_name
                    └── 1.0.0  # workflow_version, THIS IS WORKFLOW_PATH
    """
    if pipeline is None or job_partiption_key is None or workflow_name is None or workflow_version is None:
        exit(1)

    if len(pipeline) == 0 or len(job_partiption_key) == 0 or len(workflow_name) == 0 or len(workflow_version) == 0:
        exit(1)

    # get current working direcotry first
    cwd = get_workdir()
    path_list = cwd.split(os.sep)
    while not path_list.pop().startswith('account.'):
        pass

    if len(path_list) == 0:
        exit(1)  # should never happen

    jthome = os.sep.join(path_list)
    return os.sep.join([jthome,'data', 'pipeline.%s' % pipeline,
                                job_partiption_key, workflow_name,
                                workflow_version])


def get_input_path(pipeline, job_partiption_key, workflow_name, workflow_version):
    return os.sep.join([get_workflow_path(pipeline, job_partiption_key, workflow_name, workflow_version), 'input'])


def get_output_path(pipeline, job_partiption_key, workflow_name, workflow_version):
    return os.sep.join([get_workflow_path(pipeline, job_partiption_key, workflow_name, workflow_version), 'output'])


def get_reference_path(pipeline, job_partiption_key, workflow_name, workflow_version):
    return os.sep.join([get_workflow_path(pipeline, job_partiption_key, workflow_name, workflow_version), 'reference'])
