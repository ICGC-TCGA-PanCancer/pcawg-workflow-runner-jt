import os
import tarfile
from .pcawg_workflow import PcawgWorkflow
import shutil
import requests
import json
import subprocess

GitRepo = "https://github.com/ICGC-TCGA-PanCancer/pcawg-snv-indel-annotation"
Version = "1.0.0"
WorkflowFileName = "pcawg_annotate_wf.cwl"


class PcawgSnvIndelAnnotation(PcawgWorkflow):
    '''
    TODO: to be implemented
    '''
    def __init__(self, version, icgc_donor_id, local_input_dir):
        super(PcawgSnvIndelAnnotation, self).__init__(icgc_donor_id, local_input_dir)
        self._wf_version = version if version else Version
        self._wf_name = 'pcawg-snv-indel-annotation'
        self._git_repo = GitRepo
        self._wf_file_name = WorkflowFileName

    def _download_ref_data(self):
        print('download reference data: %s, version: %s' % (self.wf_name, self.wf_version))

        # Download Homo_sapiens_assembly19.fasta file and move it under local_input_dir/public
        requests.get('https://dcc.icgc.org/api/v1/download?fn=/PCAWG/reference_data/pcawg-broad/pcawg_broad_public_refs_full.tar.gz')
        tar = tarfile.open("pcawg_broad_public_refs_full.tar.gz", "r:gz")
        tar.extractall()
        tar.close()
        shutil.move('public',self.local_input_dir)

    def _download_input_data(self):
        re = requests.get('https://dcc.icgc.org/api/v1/repository/files?filters={"donor":{"id":{"is":["%s"]}},"file":{"study":{"is":["PCAWG"]}}}&size=300' % (self.icgc_donor_id))
        response = re.text
        for hit in json.loads(response):
            for file_copy in hit.get('fileCopies'):
                if file_copy.get('repoCode') == 'collaboratory' and file_copy.get('fileFormat') in ['VCF','BAM']:
                    subprocess.check_output(['icgc-storage-client','download','--object-id',file_copy.get('repoFileId'),'--profile','collab','--output-dir',self.local_input_dir])
                    break

        print('download input data for specified ICGC donor: %s, local: %s' %
              (self.icgc_donor_id, self.local_input_dir))

    def _generate_job_json(self):
        vcfs = []
        vcf_paths = []
        for f in [f for f in os.listdir('.') if os.path.isfile(f)]:
            if f.endswith('.vcf.gz'):
                vcfs.append(f)
                vcf_paths.append({"path":os.path.join(self.local_input_dir,f),"class": "File"})

        job_json = {
            "refFile": {
                "path": "%s/public/Homo_sapiens_assembly19.fasta" % (self.local_input_dir),
                "class": "File"
            },
            "tumours": {
                "associatedVcfs": vcfs
            },
            "out_dir": "/var/spool/cwl",
            "inputFileDirectory": {
                "class": "Directory",
                "path": "/media/sshorser/Data/oxog_test_data_2/%s/files_for_workflow" %(self.icgc_donor_id),
                "location": "/media/sshorser/Data/oxog_test_data_2/%s/files_for_workflow" %(self.icgc_donor_id)
            },
            "oxogVCFs": vcf_paths
        }
        print('generate job json: %s' % self.wf_name)
