#!/usr/bin/env python3
import os
import argparse
import logging
import logging.config
from src import otoscrapper

parser = argparse.ArgumentParser(
    prog = "OtoDom - offers grabber",
    description = "Scrapper for offers from otodom.pl and saves as CSV",
    epilog = "Crafted by k1k9")

parser.add_argument('-t', '--type', help='Enter A/a for apartments h/H for houses',
                    required=True, metavar="type", dest='type', choices=['h','A','H','a'])
parser.add_argument('-p', '--province', help="Enter a province in polish.",
                    required=True, metavar='province', dest='province',
                    choices=["dolnoslaskie", "kujawsko--pomorskie", "lodzkie", "lubelskie", "lubuskie", "malopolskie",
                             "mazowieckie",'opolskie','podkarpackie','podlaskie',"pomorskie","slaskie","swietokrzyskie",
                             "warminsko--mazurskie","wielkopolskie","zachodniopomorskie"])
parser.add_argument('-c', '--city', help='Entry a city in Poland',
                    required=True, metavar='city', dest='city')
parser.add_argument('-o', '--offer', help="Enter offer type: buy / rent",
                    required=True, metavar="offer", dest="offer", choices=["buy", "rent"])
parser.add_argument('-d', '--distance', help="Distance from center of city in km", default=0,
                    required=False, metavar="distance_km", dest="distance", choices=[0,5,10,15,25,50,75])
parser.add_argument('--district', help="District of city", metavar="district", dest="district")
args = parser.parse_args()
logging.config.fileConfig(fname='config.log', disable_existing_loggers=False)
log = logging.getLogger(__name__)

def main(args):
    # Printing motd
    os.system('cls' if os.name == 'nt' else 'clear')
    with open('motd', 'r') as f:
        for l in f: print(l, end="")
    otoscrapper.Runner(args)


if __name__ == '__main__':
    main(args)
