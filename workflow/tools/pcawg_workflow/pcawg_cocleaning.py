import os
import requests
from .pcawg_workflow import PcawgWorkflow
from ..utils import download_file_from_url, download_file_from_gnos, extract_gz_file

GitRepo = "https://github.com/ICGC-TCGA-PanCancer/pcawg-gatk-cocleaning"
Version = "0.1.1"
WorkflowFileName = "gatk-cocleaning-workflow.cwl"


def get_file_copies(donor_id, repo_type, tumour_normal):
    copies = []
    for hit in requests.get('https://dcc.icgc.org/api/v1/repository/files?filters={"donor":{"id":{"is":["%s"]}},"file":{"study":{"is":["PCAWG"]}}}&size=300' % (donor_id)):
        for file_copy in hit.get('fileCopies'):
            if file_copy.get('repoType') == repo_type and tumour_normal in hit.get('donors')[0].get('specimen_type'):
                copies.append(file_copy)
    return copies


class PcawgCocleaning(PcawgWorkflow):
    def __init__(self, version, icgc_donor_id, local_input_dir):
        super(PcawgCocleaning, self).__init__(icgc_donor_id, local_input_dir)
        self._wf_version = version if version else Version
        self._wf_name = 'pcawg-oxog-filter'
        self._git_repo = GitRepo
        self._wf_file = os.path.join(os.getcwd(), "%s-%s" % (self.wf_name, self.wf_version), WorkflowFileName)
        self._job_file = os.path.join(os.getcwd(), 'job.json')

    def _download_ref_data(self):
        # Download genome.fa.gz file
        download_file_from_url('https://dcc.icgc.org/api/v1/download?fn=/PCAWG/reference_data/pcawg-bwa-mem/genome.fa.gz', os.getcwd())

        # Download genome.dict file
        download_file_from_url('https://dcc.icgc.org/api/v1/download?fn=/PCAWG/reference_data/pcawg-bwa-mem/genome.dict', os.getcwd())

        # Download 1000G_phase1.indels.hg19.sites.fixed.vcf.gz file
        download_file_from_url('https://dcc.icgc.org/api/v1/download?fn=/PCAWG/reference_data/pcawg-gatk-cocleaning/1000G_phase1.indels.hg19.sites.fixed.vcf.gz', os.getcwd())

        # Download Mills_and_1000G_gold_standard.indels.hg19.sites.fixed.vcf.gz file
        download_file_from_url('https://dcc.icgc.org/api/v1/download?fn=/PCAWG/reference_data/pcawg-gatk-cocleaning/Mills_and_1000G_gold_standard.indels.hg19.sites.fixed.vcf.gz', os.getcwd())

        # Extract genome.fa.gz file
        extract_gz_file(os.path.join(os.getcwd(),'genome.fa.gz'),os.getcwd())


    def _download_input_data(self):
        # Find the normal file copy to download from GNOS from the api
        normal_file_copy = get_file_copies(self.icgc_donor_id,'GNOS','normal')[0]

        # Find the tumour file copy to download from GNOS from the api
        tumour_file_copy = get_file_copies(self.icgc_donor_id,'GNOS','tumour')[0]

        # Download the normal file from GNOS
        if not os.path.isfile(os.path.join(os.getcwd(),normal_file_copy.get('fileName'))):
            download_file_from_gnos('', "%s%s%s" % (normal_file_copy.get('repoBaseUrl'),normal_file_copy.get('repoDataPath'), normal_file_copy.get('repoDataBundleId')),os.getcwd())

        # Download the tumour file from GNOS
        if not os.path.isfile(os.path.join(os.getcwd(), tumour_file_copy.get('fileName'))):
         download_file_from_gnos('', "%s%s%s" % (tumour_file_copy.get('repoBaseUrl'),tumour_file_copy.get('repoDataPath'), tumour_file_copy.get('repoDataBundleId')),os.getcwd())


    def _generate_job_json(self):
        return {
            'tumor_bam': {
                'location': os.path.join(os.getcwd(),get_file_copies(self.icgc_donor_id,'GNOS','tumour')[0].get('fileName')),
                'class': "File"
            },
            'normal_bam': {
                'location': os.path.join(os.getcwd(),get_file_copies(self.icgc_donor_id,'GNOS','normal')[0].get('fileName')),
                'class': "File"
            },
            'reference': {
                'class': 'File',
                'location': os.path.join(os.getcwd(),'genome.fa')
            },
            'knownIndels': [
                {
                    'class': 'File',
                    'location': os.path.join(os.getcwd(), '1000G_phase1.indels.hg19.sites.fixed.vcf.gz')
                },
                {
                    'class': 'File',
                    'location': os.path.join(os.getcwd(), 'Mills_and_1000G_gold_standard.indels.hg19.sites.fixed.vcf.gz')
                }
            ],
            'knownSites': [
                {
                    'class': 'File',
                    'location': os.path.join(os.getcwd(),'dbsnp_132_b37.leftAligned.vcf.gz')
                }
            ]
        }
