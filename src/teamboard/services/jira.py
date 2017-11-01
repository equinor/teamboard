from encodings.base64_codec import base64_encode

from agithub.base import API, ConnectionProperties, Client


class Jira(API):
    def __init__(self, url, user=None, passwd=None, basic_token=None, **kwargs):
        extra_headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        if user is not None and passwd is not None:
            user_pass = bytes("%s:%s" % (user, passwd), 'utf-8')
            basic_token = base64_encode(user_pass)

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
