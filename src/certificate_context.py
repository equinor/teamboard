import ssl
import os


def _is_certificate(pem_file, folder='certificates'):
    path = os.path.join(folder, pem_file)
    return pem_file != 'cert.pem' and os.path.isfile(path) and pem_file.endswith('.pem')


def _bundle_certificates(name, path='certificates'):
    pem_files = [pem_file for pem_file in os.listdir(path) if _is_certificate(pem_file, folder=path)]

    bundle = b""
    for pem_file in pem_files:
        with open('certificates/%s' % pem_file, 'rb') as f:
            bundle += f.read()

    with open('certificates/%s.pem' % name, 'wb') as f:
        f.write(bundle)


def _create_https_context(**kwargs):
    cert_pem = 'certificates/bundle.pem'
    if not os.path.exists(cert_pem):
        _bundle_certificates(name='bundle')

    context = ssl.create_default_context(**kwargs)
    context.load_verify_locations(cafile=cert_pem)
    return context


def initialize_certificate_context():
    ssl._create_default_https_context = _create_https_context
