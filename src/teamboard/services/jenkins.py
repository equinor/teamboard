from agithub.base import API, ConnectionProperties, Client
from encodings.base64_codec import base64_encode


class Jenkins(API):
    def __init__(self, url, user=None, token=None, **kwargs):
        extra_headers = {
        }

        path = None
        if '/' in url:
            url, path = url.split("/", maxsplit=1)

        if user is not None and token is not None:
            user_token = bytes("%s:%s" % (user, token), 'utf-8')
            basic_token = base64_encode(user_token)
            auth = "Basic %s" % str(basic_token)
            extra_headers['authorization'] = auth

        props = ConnectionProperties(
            api_url=kwargs.pop('api_url', '%s' % url),
            secure_http=True,
            extra_headers=extra_headers,
            url_prefix='/%s' % path
        )

        self.setClient(Client(**kwargs))
        self.setConnectionProperties(props)


if __name__ == '__main__':
    j = Jenkins('ci.opm-project.org')

    print(j.view.All.get(pretty=True))
