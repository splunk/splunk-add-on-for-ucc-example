from test_ta_mark import is_remote_test
from pytest_splunk_addon.helmut.ssh.utils import SSHFileUtils
from pytest_splunk_addon.helmut.ssh.file import SSHFile
import tempfile
import pytest
import shutil
import os


class TASSHFile(SSHFile):
    def _retrieve_file(self):
        self._path = self._get_random_file()
        # No need to fetch the file, we're going to truncate it anyway
        if "w" in self._mode and "+" in self._mode:
            return
        try:
            self._file_utils.retrieve(self._remote_path, self._path)
        except Exception:
            self._raise_exception_unless_create()

    def _send_file(self):
        self._file_utils.send(self._path, self._remote_path)

    @classmethod
    def remove(cls, conn, path):
        conn.file_utils.delete_file(path)


class TestFileHelper:
    def __init__(self, conn):
        self.file_set = set()
        self._conn = conn

    def get_file_object(self, file_path, mode="r"):
        if is_remote_test():
            return TASSHFile(self._conn, file_path, mode)
        else:
            return file(file_path, mode)

    def remove(self, path):
        if is_remote_test():
            return TASSHFile.remove(self._conn, path)
        else:
            return os.remove(path)

    def remove_dir(self, path):
        if is_remote_test():
            utils = self._get_remote_file_utils()
            return utils.force_remove_directory(path)
        else:
            shutil.rmtree(path)

    def clean(self):
        for temp in self.file_set:
            temp.close()

    def _new_temp_file(self):
        """
        :return: the new temp file name
        """
        temp = tempfile.NamedTemporaryFile()
        self.file_set.add(temp)
        return temp.name

    def _get_remote_file_utils(self):
        conn = self._conn
        return SSHFileUtils(conn)

    def isfile(self, path):
        if is_remote_test():
            utils = self._get_remote_file_utils()
            return utils.isfile(path)
        else:
            return os.path.isfile(path)

    def isdir(self, path):
        if is_remote_test():
            utils = self._get_remote_file_utils()
            return utils.isdir(path)
        else:
            return os.path.isdir(path)

    def create_dir(self, path):
        if is_remote_test():
            utils = self._get_remote_file_utils()
            return utils.create_directory(path)
        else:
            return os.mkdir(path)

    def retrieve(self, path):
        """
        if remote, then copy the remote file to local
        if not remot, then return the path itself
        :param path: the file that want to get
        :return: local_path the copied file path
        """
        if is_remote_test():
            temp_path = self._new_temp_file()
            utils = self._get_remote_file_utils()
            utils.retrieve(path, temp_path)
            return temp_path
        else:
            return path
