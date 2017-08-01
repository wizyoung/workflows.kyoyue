# coding: utf-8
import argparse
from PIL import Image
import qrcode
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('query', nargs='?', default=None)
args = parser.parse_args()
query = args.query.split('bound')[0]

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_Q,
)
qr.add_data(query)
qr.make(fit=True)

img = qr.make_image().save('ss.png')

# img = qrcode.main.make(query, error_correction=qrcode.constants.ERROR_CORRECT_Q).save('ss.png')
print os.path.join(os.getcwd(), 'ss.png')

