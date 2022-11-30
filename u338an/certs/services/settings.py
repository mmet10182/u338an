import os
from decouple import config


ROOT_CRT_PATH = config('ROOT_CRT_PATH')
CA_PATH = config('CA_PATH')
CA_KEY_FILE = os.path.join(CA_PATH, config('KEY_FILENAME'))
CA_CERT_FILE = os.path.join(CA_PATH, config('CA_FILENAME'))