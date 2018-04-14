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
