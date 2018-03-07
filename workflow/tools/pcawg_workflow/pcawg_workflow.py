import os
import logging
from abc import ABCMeta, abstractmethod
import zipfile
from io import BytesIO
import requests
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('pcawg-data-provisioner.log')
logger.addHandler(fh)


class PcawgWorkflow(object):
    __metaclass__ = ABCMeta

    def __init__(self, icgc_donor_id, local_input_dir):
        self._wf_name = None
        self._git_repo = None
        self._wf_file = None
        self._job_file = None
        self._wf_version = None
        self._icgc_donor_id = icgc_donor_id
        self._local_input_dir = local_input_dir
        self._ref_path = os.path.abspath(os.path.join(os.getcwd(), '..', '..', '..', 'reference-data'))
        self._logger = logger

    @property
    def logger(self):
        return self._logger

    @property
    def ref_path(self):
        return self._ref_path

    @property
    def wf_name(self):
        return self._wf_name

    @property
    def job_file(self):
        return self._job_file

    @property
    def wf_version(self):
        return self._wf_version

    @property
    def wf_file(self):
        return self._wf_file

    @property
    def git_repo(self):
        return self._git_repo

    @property
    def icgc_donor_id(self):
        return self._icgc_donor_id

    @property
    def local_input_dir(self):
        return self._local_input_dir

    def provision_files(self):
        # download workflow code first
        self._download_workflow_code()

        # download reference data
        self._download_ref_data()

        # download input data for specified ICGC donor
        self._download_input_data()

        # generate job_json
        self._generate_job_json()

    def _download_workflow_code(self):
        self.logger.info('download workflow code %s' % self.git_repo)

        git_download_url = "%s/archive/%s.zip" % (self.git_repo, self.wf_version)
        request = requests.get(git_download_url)
        zfile = zipfile.ZipFile(BytesIO(request.content))
        zfile.extractall(os.getcwd())

    @abstractmethod
    def _download_ref_data(self):
        pass

    @abstractmethod
    def _download_input_data(self):
        pass

    @abstractmethod
    def _generate_job_json(self):
        pass
