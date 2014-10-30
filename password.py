import string
import random

def randompassword(size):
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for x in range(0,size))

