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
    def __init__(self, workflow_type=None, metadata=dict(),
                 metadata_service=dict(), local_path=dict(), output=dict(),
                 job_file_template=dict()
                ):
        self._wf_name = None
        self._git_repo = None
        self._wf_file = None
        self._job_file = None
        self._wf_version = None
        self._wf_type = workflow_type
        self._metadata = metadata
        self._metadata_service = metadata_service
        self._local_path = local_path
        self._output = output
        self._job_file_template = job_file_template
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
    def job_file_template(self):
        return self._job_file_template

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
    def wf_type(self):
        return self._wf_type

    @property
    def metadata(self):
        self._metadata = metadata

    @property
    def metadata_service(self):
        self._metadata_service = metadata_service

    @property
    def local_path(self):
        self._local_path = local_path

    @property
    def output(self):
        self._output = output

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
