from agithub.base import API, ConnectionProperties, Client


class Travis(API):
    def __init__(self, url='travis-ci.org', travis_token=None, *args, **kwargs):
        extra_headers = {
            'accept': 'application/vnd.travis-ci.2+json',
            'user-agent': 'MyClient / 1.0.0'
        }

        if travis_token is not None:
            auth = "token %s" % travis_token
            if auth is not None:
                extra_headers['authorization'] = auth

        props = ConnectionProperties(
            api_url=kwargs.pop('api_url', 'api.%s' % url),
            secure_http=True,
            extra_headers=extra_headers,
        )

        self.setClient(Client(*args, **kwargs))
        self.setConnectionProperties(props)

    @staticmethod
    def fetch_travis_token(url, github_token):
        extra_headers = {
            'accept': 'application/vnd.travis-ci.2+json',
            'user-agent': 'MyClient / 1.0.0',
            'content-type': 'application/json'
        }

        cp = ConnectionProperties(api_url='api.%s' % url, secure_http=True, extra_headers=extra_headers)
        client = Client(connection_properties=cp)
        status, result = client.post('/auth/github', {'github_token': github_token})

        if status != 200:
            print(client.headers)
            raise Exception("Unable to fetch Travis token: %s -> %s" % (status, result))

        return result['access_token']
