import json
import requests
import os
from urllib.parse import urlparse
import subprocess
import tarfile


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
