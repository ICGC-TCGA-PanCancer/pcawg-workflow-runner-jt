import os
from .pcawg_workflow import PcawgWorkflow

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

    def _download_input_data(self):
        print('download input data for specified ICGC donor: %s, local: %s' %
              (self.icgc_donor_id, self.local_input_dir))

    def _generate_job_json(self):
        print('generate job json: %s' % self.wf_name)
