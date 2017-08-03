import http.client

from teamboard import teamboard_logger


def no_proxy(host, no_proxy_list):
    for item in no_proxy_list:
        if host.endswith(item):
            return True
    return False


def _proxify_connection(connection_class, proxy_url=None, proxy_port=None, no_proxy_list=None):
    _connection_init = connection_class.__init__

    if no_proxy_list is None:
        no_proxy_list = []

    def _monkey_init(self, host, port=None, *args, **kwargs):
        if proxy_url is not None and not no_proxy(host, no_proxy_list):
            _connection_init(self, proxy_url, proxy_port, *args, **kwargs)
            self.set_tunnel(host, port)
            teamboard_logger().debug('Connecting to %s via proxy at %s:%s' % (host, proxy_url, proxy_port))
        else:
            _connection_init(self, host, port, *args, **kwargs)
            teamboard_logger().debug('Connecting directly to %s' % host)

    connection_class.__init__ = _monkey_init


def initialize_connection_proxy(proxy_url=None, proxy_port=None, no_proxy_list=None):
    if proxy_url is not None:
        port = ':%s' % proxy_port if proxy_port is not None else ''
        teamboard_logger().info('Monkey patched proxying at %s%s' % (proxy_url, port))
        _proxify_connection(http.client.HTTPConnection, proxy_url, proxy_port, no_proxy_list)
        _proxify_connection(http.client.HTTPSConnection, proxy_url, proxy_port, no_proxy_list)
