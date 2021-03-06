import base64
import os
from pprint import pprint

CERTIFICATE_PATH = "/home/stetsenko/ksolutions/firstcard/core/certs/yandexmoney/"
acquirer_cert = "Piastrix.cer"
acquirer_cert_key = "ym_private.key.insecure"


def get_abs_path(base, path):
    return str(os.path.join(base, path))


def M2Crypto_verify(data):
    # https://www.artur-rodrigues.com/tech/2013/08/19/verifying-x509-signatures-in-python.html
    # https://penguindreams.org/blog/signature-verification-between-java-and-python/
    message = '&'.join(["{}={}".format(k, data[k]) for k in sorted(data.keys()) if k != 'signature'])

    cert_path = get_abs_path(CERTIFICATE_PATH, acquirer_cert)
    privatekey_path = get_abs_path(CERTIFICATE_PATH, acquirer_cert_key)

    from M2Crypto import X509
    str_cert = str(open(cert_path, 'r').read())
    cert = X509.load_cert_string(str_cert)
    pubkey = cert.get_pubkey()
    pubkey.reset_context(md='sha1')
    pubkey.verify_init()
    pubkey.verify_update(message.encode('utf-8'))
    result = pubkey.verify_final(base64.b64decode(data['signature']))
    print(result)


def M2Crypto_try_sign(data):
    message = '&'.join(["{}={}".format(k, data[k]) for k in sorted(data.keys()) if k != 'signature'])

    cert_path = get_abs_path(CERTIFICATE_PATH, acquirer_cert)
    privatekey_path = get_abs_path(CERTIFICATE_PATH, acquirer_cert_key)

    from M2Crypto import X509
    str_cert = str(open(cert_path, 'r').read())
    cert = X509.load_cert_string(str_cert)
    pubkey = cert.get_pubkey()
    pubkey.reset_context(md='sha1')

    pubkey.sign_init()
    pubkey.sign_update(message.encode())
    # raise SIGSEGV - error memory access
    sign = pubkey.sign_final()
    print(base64.b64encode(sign))


def cryptography_verify(data):
    message = '&'.join(["{}={}".format(k, data[k]) for k in sorted(data.keys()) if k != 'signature'])
    cert_path = get_abs_path(CERTIFICATE_PATH, acquirer_cert)
    privatekey_path = get_abs_path(CERTIFICATE_PATH, acquirer_cert_key)

    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    with open(cert_path, 'rb') as cert_file:
        data = cert_file.read()
    cert = x509.load_pem_x509_certificate(data, default_backend())
    print(cert.serial_number)
    print(cert.signature_algorithm_oid)
    pubkey = cert.public_key()
    # ValueError: Data too long for key size. Encrypt less data or use a larger key size.
    sign = pubkey.encrypt(message.encode(),
                          padding.OAEP(
                              mgf=padding.MGF1(algorithm=hashes.SHA1()),
                              algorithm=hashes.SHA1(),
                              label=None))
    print(sign)
    print(base64.b64encode(sign))


if __name__ == '__main__':
    # callback data
    data = {'amount': '0.10', 'authcode': '346541', 'created_dt': '2018-10-02T09:50:18+03:00', 'currency': 'RUB',
            'description': '25700238903235', 'eci': '05', 'is3d': '0',
            'merchant_order_id': '58c356105a1e416c8f04470a9a28e7d1', 'message': 'Success', 'mpi_result': 'NONE',
            'operation': 'authorize', 'operation_id': '36561952',
            'order_id': 'DPfD4bXNdXl0Z6wjGIgIyQ4ulLgZ..000.201810', 'responsecode': '00',
            'responsecodetext': 'Approved', 'rrn': '788405349998',
            'signature': '66410af26958a953886365d6354e27cdcc9b39b81b3fbcf475ed4f5743b0956b2ccbd4cc8325519afcac5ddb2491f6df6effed605c57b5f7a507d6dd613e7060a92f4c433cbefc8f604ba28d8c5aa23d9c8202dee951dc6a699597afc024e0f87c41c4636db5aad98943064305b3f596f87e7343cb6d5b7dd56f9ce2f8a3f7c373b53bdda3a1aa5b9a6c92423a48d2c84a9bffbf3ef8fe9add48959d81730671a96c8f49d4d7370e641d5a1a2894f3f4d73d911434443742a208882f0d4b659c8653106be65130170b72a0686e647e1befd80f4d1289ec198211c1470a5e20b4ff447692dea88aa7d07d36adee71ec7b0096420f3df4302dfd869625d57ca23b',
            'status': 'success', 'time': '2018-10-02T09:50:18+03:00'}
    pprint(data)
    # M2Crypto_verify(data)
    M2Crypto_try_sign(data)
    # cryptography_verify(data)

