
import requests
import os
import subprocess
import shutil

def download(url, source, output_file_name, keyfile=None):
    if source.startswith('http'):
        return _download_http_file(url, output_file_name)
    elif source == 'gnos':
        return _download_gnos_file(url, output_file_name, keyfile)

def _download_http_file(http_url, output_file_name):
    #os.makedirs(os.path.dirname(output_file_name), exist_ok=True)
    #r = requests.get(http_url, stream=True)
    #with open(output_file_name, 'wb') as f:
    #    for chunk in r.iter_content(chunk_size=1024):
    #        if chunk:
    #            f.write(chunk)
    return os.path.abspath(output_file_name)

def _download_gnos_file(url,output_file_name, keyfile):
    #subprocess.check_output(['gtdownload','-c',keyfile, url])
    return os.path.abspath(output_file_name)

def decompress_with_bgzip(input_tar_gz, output_dir):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    subprocess.check_output(['tar','-jxvf',input_tar_gz,'-C',output_dir])
    return os.path.abspath(output_dir)

def mv_file_to_directory(input_dir, input_file_path, output_dir):
    os.makedirs(os.path.join(output_dir,input_file_path), exist_ok=True)
    shutil.move(os.path.join(input_dir, input_file_path), output_dir)
    return os.path.abspath(os.path.join(output_dir, input_file_path))

def pipeline_download_decompress_mv(url, source,filenames, output_dir, output_type='path',keyfile=None):
    output_filename = os.path.join(os.getcwd(),"progress.tar.gz")
    downloaded_file = download(url,source, output_filename, keyfile)
    decompressed_dir = decompress_with_bgzip(downloaded_file, os.path.join(os.getcwd(),"tmp"))
    for filename in filenames:
        print(mv_file_to_directory(decompressed_dir,filename,os.path.join(os.getcwd())))

    if output_type == 'path':
        return os.path.abspath(os.path.join(output_dir,filenames[0]))
    return filenames[0]


def pipeline_download_mv(url, source, filename, output_dir, output_type='path',keyfile=None):
    downloaded_file = download(url, source, filename, keyfile)
    shutil.move(downloaded_file, output_dir)

    if output_type == 'path':
        return os.path.abspath(os.path.join(output_dir, filename))
    return filename

def pipeline_nothing(url, source, filename, output_type):
    if source == 'file':
        if output_type == 'path':
            return url.replace('file://','')
        return filename