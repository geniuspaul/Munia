import random
import string


def generate_wallet_address():
    return 'MUN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=33))