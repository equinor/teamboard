from agithub.base import API, ConnectionProperties, Client


class Jenkins(API):
    def __init__(self, url, *args, **kwargs):
        extra_headers = {
        }

        props = ConnectionProperties(
            api_url=kwargs.pop('api_url', '%s' % url),
            secure_http=True,
            extra_headers=extra_headers,
            # url_postfix='/api/json'
        )

        self.setClient(Client(*args, **kwargs))
        self.setConnectionProperties(props)


if __name__ == '__main__':
    j = Jenkins('ci.opm-project.org')

    print(j.view.All.get(pretty=True))
