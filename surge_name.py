# coding: utf-8
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('query', nargs='?', default=None)
args = parser.parse_args()

query = args.query.split('bound')[1]

print query
