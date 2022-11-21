import logging
import copy
from pytest_splunk_addon.helmut.util import rip

LOGGER = logging.getLogger()


class SplunkInstance:
    def __init__(self, splunk):
        self._splunk = splunk
        self._rest = None
        self._username = None
        self._password = None
        self._ssh_url = None
        self._conn = None
        self._splunk_home = None
        self._splunkd_port = "8089"

    @property
    def splunk(self):
        return self._splunk

    @splunk.setter
    def splunk(self, value):
        self._splunk = value

    @property
    def rest(self):
        return self._rest

    @rest.setter
    def rest(self, value):
        self._rest = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def ssh_url(self):
        return self._ssh_url

    @ssh_url.setter
    def ssh_url(self, value):
        self._ssh_url = value

    @property
    def conn(self):
        return self._conn

    @conn.setter
    def conn(self, value):
        self._conn = value

    @property
    def splunk_home(self):
        return self._splunk_home

    @splunk_home.setter
    def splunk_home(self, value):
        self._splunk_home = value

    @property
    def splunkd_port(self):
        return self._splunkd_port

    @splunkd_port.setter
    def splunkd_port(self, value):
        self._splunkd_port = value


class SplunkInstanceManager:
    DEFAULT_INSTANCE_KEY = "default_instance"

    def __init__(self, config, splunk_instance=None):
        """
        if splunk_instance is not None, will ignore config but init with splunk_instance
        :param config: dict
        :param splunk_instance: SplunkInstance
        """
        self.config = copy.copy(config)
        self._single_splunk = {}
        self._forwarder_splunk = {}
        self._indexer_splunk = {}
        self._searchhead_splunk = {}

        self.instance_type_map = {
            "single": self._single_splunk,
            "forward": self._forwarder_splunk,
            "indexer": self._indexer_splunk,
            "searchhead": self._searchhead_splunk,
        }

        if splunk_instance:
            if not splunk_instance.rest:
                splunk_instance.rest = self.create_rest(splunk_instance.splunk)
            for _instance_type in self.instance_type_map.keys():
                self._get_splunk_dict(_instance_type)[
                    self.DEFAULT_INSTANCE_KEY
                ] = splunk_instance
            return

    #     self.remote = self.config.remote
    #     instance = self.config.instance
    #     instance_common = instance['common']
    #     for key, value in instance.items():
    #         if key == 'common':
    #             continue
    #         for instance_name, instance_info in value.items():
    #             info = copy.copy(instance_common)
    #             info.update(instance_info)
    #             self.create_instance(info, key, instance_name)

    # def create_instance(self, instance_info, instance_type, instance_name):
    #     if instance_type == 'single':
    #         if self.remote:
    #             si = self.create_remote_splunk_instance(instance_info)
    #         else:
    #             si = self.create_local_splunk_instance(instance_info)
    #         for _instance_type in self.instance_type_map.keys():
    #             self._get_splunk_dict(_instance_type)[instance_name] = si
    #     else:
    #         si = self.create_remote_splunk_instance(instance_info)
    #         self._get_splunk_dict(instance_type)[instance_name] = si

    #     si.username = instance_info['splunk_username']
    #     si.password = instance_info['splunk_password']
    #     si.ssh_url = instance_info['ssh_url']
    #     si.splunk_home = instance_info['splunk_home']
    #     if (not si.ssh_url) and (not self.remote):
    #         si.ssh_url = 'localhost'
    #     si.splunk.set_credentials_to_use(username=si.username,
    #                                      password=si.password)
    #     si.splunk.start(auto_ports=True)

    #     si.rest = self.create_rest(si.splunk)

    # @staticmethod
    # def create_local_splunk_instance(instance_info):
    #     splunk = LocalSplunk(instance_info['splunk_home'])
    #     si = SplunkInstance(splunk)
    #     return si

    # @staticmethod
    # def create_remote_splunk_instance(instance_info):
    #     kwargs = {}
    #     if instance_info['ssh_port']:
    #         kwargs['port'] = int(instance_info['ssh_port'])
    #     if instance_info['ssh_username']:
    #         kwargs['user'] = instance_info['ssh_username']
    #     if instance_info['ssh_password']:
    #         kwargs['password'] = instance_info['ssh_password']
    #     if instance_info['ssh_identity']:
    #         kwargs['identity'] = instance_info['ssh_identity']
    #     conn = SSHConnection(instance_info['ssh_url'], **kwargs)
    #     splunk = TASSHSplunk(conn, instance_info['splunk_home'])

    #     si = SplunkInstance(splunk)

    #     if instance_info['splunkd_port']:
    #         splunk.set_splunkd_port(int(instance_info['splunkd_port']))
    #         si.splunkd_port = str(instance_info['splunkd_port'])

    #     si.conn = conn
    #     return si

    @staticmethod
    def create_rest(splunk):
        rest = splunk.get_rip(False, username=splunk.username, password=splunk.password)

        return rest

    def _get_splunk_dict(self, instance_type):
        if instance_type in self.instance_type_map.keys():
            LOGGER.log(logging.INFO, instance_type)
            return self.instance_type_map[instance_type]
        else:
            raise ValueError(instance_type)

    def refresh_all_splunk(self):
        for instances_map_value in self.instance_type_map.values():
            for instance in instances_map_value.values():
                instance.refresh_splunk()

    @property
    def single_splunk(self):
        return list(self._single_splunk.values())[0]

    @property
    def single_splunk_list(self):
        return self._single_splunk.values()

    @property
    def forwarder_splunk(self):
        return list(self._forwarder_splunk.values())[0]

    @property
    def forwarder_splunk_list(self):
        return self._forwarder_splunk.values()

    @property
    def indexer_splunk(self):
        return list(self._indexer_splunk.values())[0]

    @property
    def indexer_splunk_list(self):
        return self._indexer_splunk.values()

    @property
    def searchhead_splunk(self):
        return list(self._searchhead_splunk.values())[0]

    @property
    def searchhead_splunk_list(self):
        return self._searchhead_splunk.values()
