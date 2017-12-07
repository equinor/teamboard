from agithub.base import API, ConnectionProperties, Client


class Slack(API):
    def __init__(self, token, *args, **kwargs):
        extra_headers = {
            'authorization': 'Bearer %s' % token
        }

        props = ConnectionProperties(
            api_url=kwargs.pop('api_url', 'slack.com'),
            secure_http=True,
            extra_headers=extra_headers,
            url_prefix='/api'
        )

        self.setClient(Client(*args, **kwargs))
        self.setConnectionProperties(props)
