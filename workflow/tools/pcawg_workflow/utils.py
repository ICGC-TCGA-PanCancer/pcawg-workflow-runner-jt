import json
import requests
import os
import subprocess
import re


def hyphen_to_camel_case(snake_str):
    components = snake_str.split('-')
    return ''.join(x.title() for x in components)


def download_file_from_url(url, output_dir, filename=None, force=False):
    if os.path.isfile(os.path.join(output_dir, filename)) and force == False:
        return

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(os.path.join(output_dir, filename), 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    return os.path.join(output_dir, filename)


def download_file_from_gnos(credentials_file, file_path, output_dir):
    try:
        subprocess.call(['docker'])
    except OSError as e:
        raise Exception("Docker is not installed.")

    subprocess.check_output(['docker','pull','quay.io/pancancer/gtclient:0.1'])
    subprocess.check_output(['docker','run','-v',output_dir+':/output','-v',os.path.dirname(credentials_file)+':/app','quay.io/pancancer/gtclient:0.1','gtdownload','-p','/output','-c','/app/'+os.path.basename(credentials_file), file_path])


def extract_bgzip_file(file_path, output_dir, force=False):
    if not file_path.endswith('.gz'):
        raise Exception("the file name is not a .gz file: "+file_path)
    if os.path.isfile(os.path.join(output_dir,file_path.strip('.gz'))) and force == False:
        return
    subprocess.check_output(['bgzip','-d',file_path])


def parse_placeholder(placeholder):
    """
    Create a placeholder dict from a placeholder name. The placeholder dict contains more informations for later.
    :param placeholder: A placeholder string
    :return: A dict
    """
    _placeholder = placeholder.strip('{{').strip('}}').replace(' ','').split('|')
    base = _placeholder[0]
    filters = []

    for filter in _placeholder[1:]:
        filter_name = filter.split(':')[0]
        filters.append({'name':filter_name,'params':[filter.replace(filter_name+':','')]})

    return {
        'template': "{{"+placeholder+"}}",
        'key': base.replace('.*',''),
        'base': base,
        'filters': filters,
        'type': "array" if base.endswith('*') else "string"
    }


def validate_filter(filter, value):
    """
    Validates the filter applied to the placeholder
    :param filter: The filter string
    :param value: The value to check against the filter
    :return:
    """
    if 'regex' in filter.get('name'):
        return bool(re.match(filter.get('params')[0],value))
    return False


def replace_placeholder(placeholder, dict, text):
    """
    Replace the placeholder with the corresponding dict dict value in the text
    :param placeholder: Can be string or array placeholder
    :param dict:
    :param text:
    :return:
    """
    value = dict[placeholder.get('key')]

    if placeholder.get('type') is 'string':
        return _replace_string_placeholder(placeholder, value, text)

    if placeholder.get('type') is 'array':
        for v in value:
            for filter in placeholder.get('filters'):
                filter_error = ('|').join([filter.get('name')] + filter.get('params'))
                if validate_filter(filter, v):
                    raise Exception("Invalid variable: %s:%s - Validator: %s" % (placeholder.get('key'), value, str(filter_error)))
        return text.replace(placeholder.get('template'),str(value))

def _replace_string_placeholder(placeholder, value, text):
    """
    Replace a string placeholder in a text
    :param placeholder:
    :param value:
    :param text:
    :return:
    """
    if placeholder.get('type') is 'string':
        for filter in placeholder.get('filters'):
            if not validate_filter(filter, value):
                filter_error = ('|').join([filter.get('name')]+filter.get('params'))
                raise Exception("Invalid variable: %s:%s - Validator: %s" % (placeholder.get('key'), value, str(filter_error)))
        return text.replace(placeholder.get('template'), value)


def generate_job_from_template(values, template_file, output_file):
    """
    Generates a job.json from the corresponding template
    :param values:
    :param template_file:
    :param output_file:
    :return:
    """
    with open(template_file,'r') as f:
        #Read the text in the file
        text = f.read().replace("\n","").replace(" ",'')

        # Find the list of placeholders in the text
        placeholders_list = list(set(re.findall(r"\{\{(\w+(?:\.\*)?\|?(?:regex:[a-zA-Z0-9*.://-]+)?)\}\}", text)))

        #Create a placeholders array and parse the placeholders to objects
        placeholders = []
        for placeholder_name in placeholders_list:
            placeholders.append(parse_placeholder(placeholder_name))

        # Replace the placeholders in the text
        for placeholder in placeholders:
            text = replace_placeholder(placeholder, values, text)

        text = text.replace("'",'"')

        # Output the new generated text in the job.json
        with open(output_file, 'w') as f:
            json.dump(json.loads(text), f, indent=4, sort_keys=True)

