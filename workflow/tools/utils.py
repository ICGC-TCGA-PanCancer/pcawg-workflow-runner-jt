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


def hyphen_to_camel_case(snake_str):
    components = snake_str.split('-')
    return ''.join(x.title() for x in components)