import requests

GRAPH_URL = "https://graph.microsoft.com/v1.0"


class DataGenerator:
    def __init__(self, tenant_id, client_id, client_secret):
        """
        Init method
        :param tenant_id: The UUID which point to the AD containing your application
        :param client_id: The client id which is automatically generated when registering with Azure AD
        :param client_secret: The password for client_id
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()
        self.headers = {
            "Authorization": "Bearer %s" % self.access_token,
            "Content-type": "application/json",
        }
        self.session = requests.Session()
        self.session.hooks = {
            "response": lambda res, *args, **kwargs: res.raise_for_status()
        }

    def get_access_token(self):
        """
        Get access token
        :return access token
        """
        response = requests.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
            data=f"scope=https://graph.microsoft.com/.default&grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ).json()
        return response.get("access_token")


class AuditADGen(DataGenerator):
    """
    Class to generate events for workload: AzureActiveDirectory
    """

    def __init__(self, tenant_id, client_id, client_secret):
        super(AuditADGen, self).__init__(tenant_id, client_id, client_secret)
        self.endpoint = GRAPH_URL + "/users"

    def create_user(self, payload):
        """
        Create User
        :param payload: User details to create a user
        :return response
        """
        response = self.session.post(
            self.endpoint, headers=self.headers, json=payload
        ).json()

        return response

    def delete_user(self, user_id):
        """
        Delete User
        :param user_id: user_id of the user to be deleted
        """
        response = self.session.delete(
            self.endpoint + "/{}".format(user_id), headers=self.headers
        )


class AuditSharepointGen(DataGenerator):
    """
    Class to generate events for workload: SharePoint
    """

    def __init__(self, tenant_id, client_id, client_secret):
        super(AuditSharepointGen, self).__init__(tenant_id, client_id, client_secret)
        self.endpoint = GRAPH_URL + "/sites"

    def get_site(self):
        """
        Get Site
        :return response
        """
        response = self.session.get(
            self.endpoint + "/splunkcdcdev.sharepoint.com:/sites/O365_TA_DO_NOT_DELETE",
            headers=self.headers,
        ).json()

        return response

    def create_list(self, site_id, payload):
        """
        Create List
        :param site_id: site_id in which List is to be created
        :param payload: List details to create a List
        :return response
        """
        response = self.session.post(
            self.endpoint + "/{}/lists".format(site_id),
            headers=self.headers,
            json=payload,
        ).json()

        return response

    def delete_list(self, site_id, list_to_be_deleted):
        """
        Delete List
        :param site_id: site_id in which List is to be deleted
        :param list_to_be_deleted: List name to be deleted
        """
        response = self.session.delete(
            self.endpoint + "/{}/lists/{}".format(site_id, list_to_be_deleted),
            headers=self.headers,
        )


class AuditExchangeGen(DataGenerator):
    """
    Class to generate events for workload: Exchange
    """

    def __init__(self, tenant_id, client_id, client_secret):
        super(AuditExchangeGen, self).__init__(tenant_id, client_id, client_secret)
        self.endpoint = GRAPH_URL + "/groups"

    def create_group(self, payload):
        """
        Create Group
        :param payload: Group details to create a group
        :return response
        """
        response = self.session.post(
            self.endpoint, headers=self.headers, json=payload
        ).json()

        return response

    def delete_group(self, group_id):
        """
        Delete Group
        :param group_id: group_id of the group to be deleted
        """
        response = self.session.delete(
            self.endpoint + "/{}".format(group_id), headers=self.headers
        )
