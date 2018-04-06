import json
import requests
import os
from urllib.parse import urlparse
import subprocess
import tarfile


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





def download_file_from_url(url, output_dir, force=False):
    filename = os.path.basename(urlparse(url))

    if os.path.join(output_dir,filename) and force == False:
        return

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(os.path.join(output_dir, filename)) as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    return os.path.join(output_dir, filename)

def download_file_from_gnos(credentials_file, file_path, output_dir):
    try:
        subprocess.call(['docker'])
    except OSError as e:
        raise Exception("Docker is not installed.")

    subprocess.check_output(['docker','pull','quay.io/pancancer/gtclient'])
    subprocess.check_output(['docker','run','quay.io/pancancer/gtclient','gtdownload','-p',output_dir,'-c',credentials_file, file_path])

def extract_gz_file(file_path, output_dir, force=False):
    if not file_path.endswith('.gz'):
        raise Exception("the file name is not a .gz file: "+file_path)
    if os.path.isfile(os.path.join(output_dir,file_path.strip('.gz'))) and force == False:
        return
    tar = tarfile.open(file_path, "r:gz")
    tar.extractall(path=output_dir)
    tar.close()