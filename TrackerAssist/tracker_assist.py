import requests
from typing import Union

VALID_FIELDS = {
    'ASSET_FIELDS': ('Name', 'Description', 'Status', 'Owner', 'HeldBy', 'Contact'),
    'QUEUE_FIELDS': ('Name', 'Description', 'Lifecycle', 'SubjectTag', 'CorrespondAddress', 'CommentAddress'),
    'TICKET_FIELDS': ('Queue', 'Status', 'Owner', 'Requestors', 'Cc', 'AdminCc', 'Content', 'ContentType'),
    'USER_FIELDS': ('EmailAddress', 'RealName', 'NickName', 'Gecos', 'Lang', 'Timzone', 'FreeformContactInfo',
                    'SetEnabled', 'Enabled', 'SetPrivileged', 'CurrentPass', 'Pass1', 'Pass2', 'Organization',
                    'Address1', 'Address2', 'City', 'State', 'Zip', 'Country', 'HomePhone', 'WorkPhone',
                    'MobilePhone', 'PagerPhone', 'Comments')
}


class RTClient:

    def __init__(self, server: str, token: str = None, username: str = None,
                 password: str = None, verify_cert: bool = True):
        """
        :param server: Define your RT server along with port (IE, http://127.0.0.1:8000)
        :param token: Supply the token you provisioned via the Web UI
        :param verify_cert: Specify whether you'd like SSL verification enabled

        Example: rt_client = RTClient(<server>, <token>, verify_cert=False)
        """
        self.server = server.rstrip('/') + '/REST/2.0'  # Remove trailing whack(s) if any are present
        self.session = requests.session()
        self.session.verify = verify_cert

        # If a token is supplied, use it; If not, authenticate using supplied credentials.
        if token:
            self.session.headers = {'Authorization': f'token {token}',
                                    'Content-Type': 'application/json'}

        elif username and password:
            data = {'user': username, 'pass': password}
            self.session.post(server, data=data)

        else:
            print("Error! No token or credentials supplied - Transactions may fail!")

    def get_queues(self) -> dict:
        """
        View all queues your account has access to.
        :return:
        """
        response = self.session.get(self.server + '/queues/all')

        if response.status_code == 200:
            return response.json()

    def get_queue(self, queue_id: Union[str, int]) -> dict:
        """
        View a single queue's attributes by supplying its unique identifier.
        :param queue_id: Unique queue identifier
        :return:
        """

        response = self.session.get(self.server + f'/queue/{queue_id}')

        if response.status_code == 200:
            return response.json()

    def get_queue_history(self, queue_id: Union[str, int]) -> dict:
        response = self.session.get(self.server + f'/queue/{queue_id}')

        if response.status_code == 200:
            return response.json()

    def create_queue(self, name: str, **kwargs) -> bool:
        """
        Create a queue by supplying (at the very least) a name which will act as the queue's title.
        :param name: Name by which the queue will be known.
        :param kwargs: Valid arguments: ''Description', 'Lifecycle', 'SubjectTag','CorrespondAddress', 'CommentAddress'
        :return:
        """
        for argument in kwargs.keys():
            if argument not in VALID_FIELDS['QUEUE_FIELDS']:
                print(f"Error: {argument} not a valid queue field.\n"
                      f"Valid queue fields: {', '.join(VALID_FIELDS['QUEUE_FIELDS'])}")
                return False

        payload = {
            'Name': name
        }

        payload.update(kwargs)

        response = self.session.post(self.server + '/queue', json=payload)

        return response.status_code == 201

    def update_queue(self, queue_id: Union[str, int], **kwargs) -> bool:
        """
        Update a queue by supplying its unique identifier and a series of keyword arguments
        :param queue_id: Unique identifier for the queue.
        :param kwargs: Valid arguments: ''Description', 'Lifecycle', 'SubjectTag','CorrespondAddress', 'CommentAddress'
        :return:
        """
        for argument in kwargs.keys():
            if argument not in VALID_FIELDS['QUEUE_FIELDS']:
                print(f"Error: {argument} not a valid queue field.\n"
                      f"Valid queue fields: {', '.join(VALID_FIELDS['QUEUE_FIELDS'])}")
                return False

        response = self.session.put(self.server + f'/queue/{queue_id}', json=kwargs)

        return response.status_code == 201

    def disable_queue(self, queue_id: Union[str, int]) -> bool:
        """
        Disable a single queue.
        :param queue_id: Unique identifier for the target queue.
        :return:
        """
        response = self.session.delete(self.server + f'/queue/{queue_id}')

        return response.status_code == 201

    def get_ticket(self, ticket_id: Union[str, int]) -> dict:
        """
        Get a single ticket's details.
        :param ticket_id: Value may be a string or integer due to flexibility of f-string interpolation.
        :return:
        """
        response = self.session.get(self.server + f'/ticket/{ticket_id}')

        if response.status_code == 200:
            return response.json()

    def get_ticket_history(self, ticket_id: Union[str, int]) -> dict:
        """
        View the transaction history for a single ticket.
        :param ticket_id: Value may be a string or integer due to flexibility of f-string interpolation.
        :return:
        """
        response = self.session.get(self.server + f'/ticket/{ticket_id}/history')

        if response.status_code == 200:
            return response.json()

    def create_ticket(self, subject: str, queue: str, custom_fields: dict = None, **kwargs) -> str:
        """
        Create a ticket with supplied parameters (Only Subject and Queue are required).
        :param subject: Title of your ticket.
        :param queue: Queue to which your ticket will belong.
        :param custom_fields: Supply custom fields in dict format (IE, {'CF.{IPv4}': '8.8.8.8}
        :param kwargs: Any other standard (non-custom) fields may be defined as keyword arguments.
        :return:
        """
        payload = {
            'Queue': queue,
            'Subject': subject
        }

        if custom_fields:
            payload['CustomFields'] = custom_fields

        if kwargs:
            payload.update(kwargs)

        response = self.session.post(self.server + '/ticket', json=payload)

        if response.status_code == 201:
            return response.json()['_url']

    def update_ticket(self, ticket_id: Union[str, int], custom_fields: dict = None, **kwargs) -> bool:
        """
        Edit a single ticket to which you have access.
        :param ticket_id: Value may be a string or integer due to flexibility of f-string interpolation.
        :param custom_fields: Supply custom fields in dict format (IE, {'CF.{IPv4}': '8.8.8.8}
        :param kwargs: Any other standard (non-custom) fields may be defined as keyword arguments.
        :return:
        """
        if custom_fields:
            payload = {'CustomFields': custom_fields}
            payload.update(kwargs)
        else:
            payload = kwargs

        response = self.session.put(self.server + f'/ticket/{ticket_id}', json=payload)

        return response.status_code == 200

    def post_comment(self, ticket_id: Union[str, int], comment: str, content_type: str = 'text/plain',
                     custom_fields: dict = None, **kwargs) -> bool:
        """
        Add a comment to a single ticket by specifying the unique ticket identifier.
        :param ticket_id: Value may be a string or integer due to flexibility of f-string interpolation.
        :param comment: Text you wish to be added as a comment to the target ticket.
        :param content_type: Maybe text/plain or text/html
        :param custom_fields: Any other standard (non-custom) fields may be defined as keyword arguments.
        :param kwargs:
        :return:
        """
        payload = {'Content': comment,
                   'ContentType': content_type}

        if custom_fields:
            payload['CustomFields'] = custom_fields

        payload.update(kwargs)

        response = self.session.post(self.server + f'/ticket/{ticket_id}/comment', json=payload)

        return response.status_code == 201

    def upload_file(self, ticket_id: Union[str, int], file_name: str, file_path: str) -> bool:
        """
        Upload a file to a single ticket. This method is still a little buggy for now.
        :param ticket_id: Value may be a string or integer due to flexibility of f-string interpolation.
        :param file_name: Name of file.
        :param file_path: Absolute or relative path where the target file may be found.
        :return:
        """
        self.session.headers['Content-Type'] = 'multipart/form-data'

        files = {'file': (file_name, open(file_path, 'rb'))}

        response = self.session.post(self.server + f'/ticket/{ticket_id}/comment',
                                     json={'Attachment': f'{file_name}'}, files=files)

        self.session.headers['Content-Type'] = 'application/json'

        return response.status_code == 200

    def delete_ticket(self, ticket_id: Union[str, int]) -> bool:
        """
        Delete a single ticket by ID (if you have permissions to do so.)
        :param ticket_id: Value may be a string or integer due to flexibility of f-string interpolation.
        :return:
        """
        response = self.session.delete(self.server + f'/ticket/{ticket_id}')

        return response.status_code == 201

    def raw_search(self, ticket_sql: str) -> dict:
        """
        The easiest way to get the hang of this is to use RT's Query Builder, then click 'Advanced'.
        :param ticket_sql: You may supply the output here as a string. IE, "Queue = 'General'"
        :return:
        """
        params = {
            'query': ticket_sql
        }

        response = self.session.get(self.server + f'/tickets', params=params)

        if response.status_code == 200:
            return response.json()

    def get_asset(self, asset_id: Union[str, int]) -> dict:
        """
        Retrieve metadata related to a target asset.
        :param asset_id: Unique asset identifier - May be string or integer.
        :return:
        """

        response = self.session.get(self.server + f'/asset/{asset_id}')

        if response.status_code == 200:
            return response.json()

    def create_asset(self, name: str, **kwargs) -> bool:
        """
        Create an asset by supplying (at least) a name by which the asset will be known.
        :param name: Title for the asset.
        :param kwargs: Valid arguments: 'Description', 'Status', 'Owner', 'HeldBy', 'Contact'
        :return:
        """

        for argument in kwargs.keys():
            if argument not in VALID_FIELDS['ASSET_FIELDS']:
                print(f"Error: {argument} not a valid asset field.\n"
                      f"Valid asset fields: {', '.join(VALID_FIELDS['ASSET_FIELDS'])}")
                return False

        payload = {
            'Name': name
        }

        payload.update(kwargs)

        response = self.session.post(self.server + '/asset', json=payload)

        return response.status_code == 201

    def update_asset(self, asset_id: Union[str, int], **kwargs) -> bool:
        """
        Update an asset's metadata by specifying its ID.
        :param asset_id: Unique asset identifier - May be string or integer.
        :param kwargs: Valid arguments: 'Name', 'Description', 'Status', 'Owner', 'HeldBy', 'Contact'
        :return:
        """

        for argument in kwargs.keys():
            if argument not in VALID_FIELDS['ASSET_FIELDS']:
                print(f"Error: {argument} not a valid asset field.\n"
                      f"Valid asset fields: {', '.join(VALID_FIELDS['ASSET_FIELDS'])}")
                return False

        response = self.session.put(self.server + f'/asset/{asset_id}', json=kwargs)

        return response.status_code == 201

    def delete_asset(self, asset_id: Union[str, int]) -> bool:
        """
        Delete an asset by specifying its ID.
        :param asset_id: Unique asset identifier - May be a string or integer.
        :return:
        """

        response = self.session.delete(self.server + f'/asset/{asset_id}')

        return response.status_code == 201

    def get_user(self, user_id: Union[str, int]) -> dict:
        """
        View a single user's metadata.
        :param user_id: Unique user identifier (may be string or integer).
        :return:
        """

        response = self.session.get(self.server + f'/user/{user_id}')

        if response.status_code == 200:
            return response.json()

    def get_user_history(self, user_id: Union[str, int]) -> dict:
        """
        View an individual user's transaction history.
        :param user_id: Unique user identifier (may be string or integer).
        :return:
        """

        response = self.session.get(self.server + f'/user/{user_id}/history')

        if response.status_code == 200:
            return response.json()

    def create_user(self, username: str, **kwargs) -> bool:
        """
        Create a user by supplying (at least) a username and a series of arguments.
        :param username: Supply a string with which this user will login to RT.
        :param kwargs: Valid arguments: 'EmailAddress', 'RealName', 'NickName', 'Gecos', 'Lang', 'Timzone',
                    'FreeformContactInfo', 'SetEnabled', 'Enabled', 'SetPrivileged', 'CurrentPass', 'Pass1', 'Pass2',
                    'Organization', 'Address1', 'Address2', 'City', 'State', 'Zip', 'Country', 'HomePhone', 'WorkPhone',
                    'MobilePhone', 'PagerPhone', 'Comments'
        :return:
        """
        for argument in kwargs.keys():
            if argument not in VALID_FIELDS['USER_FIELDS']:
                print(f"Error: {argument} not a valid user field.\n"
                      f"Valid user fields: {', '.join(VALID_FIELDS['USER_FIELDS'])}")
                return False

        payload = {'Name': username}

        payload.update(kwargs)

        response = self.session.post(self.server + '/user', json=payload)

        return response.status_code == 201

    def update_user(self, user_id: Union[str, int], **kwargs) -> bool:
        """
        Update a user by specifying their ID.
        :param user_id: Supply unique user identifier (may be string or integer).
        :param kwargs: See 'Create User' for valid keyword arguments.
        :return:
        """
        for argument in kwargs.keys():
            if argument not in VALID_FIELDS['USER_FIELDS']:
                print(f"Error: {argument} not a valid user field.\n"
                      f"Valid user fields: {', '.join(VALID_FIELDS['USER_FIELDS'])}")
                return False

        response = self.session.put(self.server + f'/user/{user_id}', json=kwargs)

        return response.status_code == 201

    def disable_user(self, user_id: Union[str, int]) -> bool:
        """
        Disable a single user by specifying their ID.
        :param user_id: Unique user identifier (may be string or integer).
        :return:
        """
        response = self.session.delete(self.server + f'/user/{user_id}')

        return response.status_code == 201

