'''
    use diffle-hellman to exchange key
'''


from common.Crypto.prime import generate_big_prime
from common.config import get_config
import hashlib
from common.utils import long_to_bytes


config = get_config()
q = config['diffle-hellman']['mod']
a = config['diffle-hellman']['base']

private = generate_big_prime(12)

my_secret = a ** private % q

def get_shared_secret(other_secret):
    '''
        用sha256散列算法截断diffle-hellman产生的共同密钥到128位(16 bytes)
    '''
    m = hashlib.sha256()
    m.update(long_to_bytes(other_secret ** private % q))
    return m.digest()

