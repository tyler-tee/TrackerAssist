import requests
from typing import Union

VALID_QUEUE_FIELDS = ('Name', 'Description', 'Lifecycle', 'SubjectTag', 'CorrespondAddress', 'CommentAddress')


class RTClient:

    def __init__(self, server: str, token: str, verify_cert: bool = True):
        """
        :param server: Define your RT server along with port (IE, http://127.0.0.1:8000)
        :param token: Supply the token you provisioned via the Web UI
        :param verify_cert: Specify whether you'd like SSL verification enabled

        Example: rt_client = RTClient(<server>, <token>, verify_cert=False)
        """
        self.server = server.rstrip('/') + '/REST/2.0'  # Remove trailing whack(s) if any are present
        self.session = requests.session()
        self.session.verify = verify_cert
        self.session.headers = {'Authorization': f'token {token}',
                                'Content-Type': 'application/json'}

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

    def create_queue(self, name: str, **kwargs) -> bool:
        """
        Create a queue by supplying (at the very least) a name which will act as the queue's title.
        :param name: Name by which the queue will be known.
        :param kwargs: Valid arguments: ''Description', 'Lifecycle', 'SubjectTag','CorrespondAddress', 'CommentAddress'
        :return:
        """
        for argument in kwargs.keys():
            if argument not in VALID_QUEUE_FIELDS:
                print(f"Error: {argument} not a valid queue field.\n"
                      f"Valid queue fields: {', '.join(VALID_QUEUE_FIELDS)}")

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
            if argument not in VALID_QUEUE_FIELDS:
                print(f"Error: {argument} not a valid queue field.\n"
                      f"Valid queue fields: {', '.join(VALID_QUEUE_FIELDS)}")

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
