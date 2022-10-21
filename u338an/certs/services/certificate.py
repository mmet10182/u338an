import os
import random

import OpenSSL
from OpenSSL import crypto
from .settings import CA_CERT_FILE, CA_KEY_FILE, ROOT_CRT_PATH
from datetime import datetime


def create_pkcs12(file_name=None, passphrase=None):
    if file_name is None:
        return 'need а file name'
    if passphrase is None:
        return 'need а passphrase'
    file_name_cer = file_name + '.cer'
    file_name_key = file_name + '.key'
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(os.path.join(ROOT_CRT_PATH, file_name_cer)).read())
    key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(os.path.join(ROOT_CRT_PATH, file_name_key)).read())
    pfx = crypto.PKCS12()
    pfx.set_privatekey(key)
    pfx.set_certificate(cert)
    pfxdata = pfx.export(passphrase=passphrase)
    certfile = '{}{}.p12'.format(ROOT_CRT_PATH, file_name)
    with open(certfile, 'wb') as f:
        f.write(pfxdata)

    return {
        'pathcert': certfile,
    }


def create_cert(cn=None, emailaddr='None'):
    print('{} {}'.format(cn, emailaddr))
    if cn is None:
        return 'cn is need'
    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(CA_CERT_FILE).read())
    ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(CA_KEY_FILE).read())

    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    # creaing the CRS request
    req = crypto.X509Req()
    req.get_subject().C = ca_cert.get_subject().C
    req.get_subject().ST = ca_cert.get_subject().ST
    req.get_subject().L = ca_cert.get_subject().L
    req.get_subject().O = ca_cert.get_subject().O
    req.get_subject().OU = ca_cert.get_subject().OU
    req.get_subject().CN = cn
    req.get_subject().emailAddress = emailaddr
    req.set_pubkey(k)
    req.sign(k, 'sha512')
    key = crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
    csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    # csr save to file
    keyfile = '{}{}.key'.format(ROOT_CRT_PATH, cn)
    with open(keyfile, 'wb') as f:
        f.write(key)

    serialnumber = random.getrandbits(64)
    csr_req = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr)
    # creating the certificate
    certs = crypto.X509()
    certs.set_serial_number(serialnumber)
    certs.gmtime_adj_notBefore(0)
    certs.gmtime_adj_notAfter(31536000)
    certs.set_subject(csr_req.get_subject())
    certs.set_issuer(ca_cert.get_subject())
    certs.set_pubkey(k)
    certs.sign(ca_key, 'sha512')
    certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, certs)
    # cer save to file
    certfile = '{}{}.cer'.format(ROOT_CRT_PATH, cn)
    with open(certfile, 'wb') as f:
        f.write(certificate)

    return {
        'pathcert': certfile,
        'pathkey': keyfile,
    }


def get_content_dir():
    path = ROOT_CRT_PATH
    content_dir = os.listdir(path)
    content_dir_attrib = dict()

    for i in content_dir:
        path_cert = '{}{}'.format(path, i)
        if os.path.isfile(path_cert):
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(path_cert).read())
            except OpenSSL.crypto.Error:
                pass
            except UnicodeDecodeError:
                pass

            valid_from = datetime.strptime(cert.get_notBefore().decode('ascii'), '%Y%m%d%H%M%SZ')
            valid_to = datetime.strptime(cert.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
            if os.path.isfile(os.path.join(path, i)):
                filename, file_extension = os.path.splitext(i)
                content_dir_attrib[i] = {'type': 'File',
                                         'filetype': file_extension,
                                         'filename': filename,
                                         'valid_from': str(valid_from),
                                         'valid_to': str(valid_to)}
            else: pass
    return content_dir_attrib