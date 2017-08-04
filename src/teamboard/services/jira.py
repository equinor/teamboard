from encodings.base64_codec import base64_encode

from agithub.base import API, ConnectionProperties, Client


class Jira(API):
    def __init__(self, url, user=None, password=None, basic_token=None, **kwargs):
        extra_headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        if user is not None and password is not None:
            basic_token = base64_encode(bytes("%s:%s" % (user, password)))

        if basic_token is not None:
            auth = "Basic %s" % str(basic_token)
            extra_headers['authorization'] = auth

        props = ConnectionProperties(
            api_url=kwargs.pop('api_url', url),
            secure_http=True,
            extra_headers=extra_headers,
            url_prefix='/rest/api/2'
        )

        self.setClient(Client())
        self.setConnectionProperties(props)
