import os
from os import listdir
import sys
from shutil import copyfile, rmtree
import requests
import json
import subprocess
from .pcawg_workflow import PcawgWorkflow

GitRepo = "https://github.com/ICGC-TCGA-PanCancer/pcawg-oxog-filter"
Version = "1.0.0"
WorkflowFileName = "pcawg_oxog_wf.cwl"


class PcawgOxogFilter(PcawgWorkflow):
    def __init__(self, version, icgc_donor_id, local_input_dir):
        super(PcawgOxogFilter, self).__init__(icgc_donor_id, local_input_dir)
        self._wf_version = version if version else Version
        self._wf_name = 'pcawg-oxog-filter'
        self._git_repo = GitRepo
        self._wf_file = os.path.join(os.getcwd(), "%s-%s" % (self.wf_name, self.wf_version), WorkflowFileName)
        self._job_file = os.path.join(os.getcwd(), 'job.json')

    def _download_ref_data(self):
        self.logger.info('download reference data: %s, version: %s' % (self.wf_name, self.wf_version))
        # since one compute node can only run one executor, the executor should always
        # have exclusive access to the ref_path
        ref_data_provision_flag_file = os.path.join(self.ref_path, 'reference-data.provisioned')
        if os.path.isfile(ref_data_provision_flag_file):
            return  # ref data provisioned already, no action needed

        rmtree(self.ref_path, ignore_errors=True)
        os.makedirs(self.ref_path)
        # download it from ICGC Data Portal
        data_url = 'https://dcc.icgc.org/api/v1/download?fn=/PCAWG/reference_data/pcawg-broad/pcawg_broad_public_refs_full.tar.gz'
        r = requests.get(data_url)
        local_file = 'pcawg_broad_public_refs_full.tar.gz'
        with open(local_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        success = True
        stdout, stderr = '', ''
        p = subprocess.Popen(["tar xf %s" % local_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        try:
            stdout, stderr = p.communicate()
        except Exception as e:
            success = False  # task failed

        if p.returncode != 0 or success is False:
            with open('tar.stdout.txt', 'w') as o:
                o.write(stdout.decode("utf-8"))
            with open('tar.stderr.txt', 'w') as e:
                e.write(stderr.decode("utf-8"))
            sys.exit(1)

        # now it must have succeeded
        open(ref_data_provision_flag_file, 'w').close()  # create the flag

    def _download_input_data(self):
        self.logger.info('download input data for specified ICGC donor: %s, local: %s' %
                         (self.icgc_donor_id, self.local_input_dir))

        # for demo purpose, we can just copy the file from local, in real world
        # input data files should be transferred to the task dir (ie, cwd)
        if (self.local_input_dir):  # assume no subfolders
            if not os.path.isabs(self.local_input_dir):
                raise Exception('Provided local directory must use absolute path!')
            for file_ in [f for f in listdir(self.local_input_dir) if os.path.isfile(os.path.join(self.local_input_dir, f))]:
                copyfile(os.path.join(self.local_input_dir, file_), os.path.join(os.getcwd(), file_))

    def _generate_job_json(self):
        input_bam = None
        input_vcfs = []
        for f in [f for f in os.listdir('.') if os.path.isfile(f)]:
            if f.endswith('.bam'):
                input_bam = f
                tumourId = os.path.splitext(input_bam)[0]
            elif f.endswith('.vcf.gz'):
                input_vcfs.append(f)

        if not input_bam or not input_vcfs:
            raise Exception('Incomplete input data files')

        job_json = {
            "refFile": {
                "path": "%s/public/Homo_sapiens_assembly19.fasta" % self.ref_path,
                "class": "File"
            },
            "out_dir": "/var/spool/cwl/",
            "refDataDir": {
                "class": "Directory",
                "path": self.ref_path,
                "location": self.ref_path
            },
            "inputFileDirectory": {
                "class": "Directory",
                "path": os.getcwd(),
                "location": os.getcwd()
            },
            "tumours":
                [
                    {
                        "tumourId": tumourId,
                        "bamFileName": input_bam,
                        "associatedVcfs": input_vcfs,
                        "oxoQScore": 38.59  ## hardcode this, TODO: get it properly from ICGC portal
                    }
                ]
        }
        with open('job.json', 'w') as j:
            j.write(json.dumps(job_json, indent=2))

        self.logger.info('Generated job json')
