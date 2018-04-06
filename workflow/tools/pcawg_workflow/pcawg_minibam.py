
from .pcawg_workflow import PcawgWorkflow

import os

GitRepo = "https://github.com/ICGC-TCGA-PanCancer/pcawg-minibam"
Version = "1.0.0"
WorkflowFileName = "pcawg_minibam_wf.cwl"


class PcawgOxogFilter(PcawgWorkflow):
    def __init__(self, version, icgc_donor_id, local_input_dir):
        super(PcawgOxogFilter, self).__init__(icgc_donor_id, local_input_dir)
        self._wf_version = version if version else Version
        self._wf_name = 'pcawg-oxog-filter'
        self._git_repo = GitRepo
        self._wf_file = os.path.join(os.getcwd(), "%s-%s" % (self.wf_name, self.wf_version), WorkflowFileName)
        self._job_file = os.path.join(os.getcwd(), 'job.json')

    def _download_ref_data(self):
        return