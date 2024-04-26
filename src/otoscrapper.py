import re
import csv
import random
import requests
import logging
from bs4 import BeautifulSoup

class Runner:

    def __init__(self, args):
        # Load arguments
        self.type = "mieszkanie" if args.type.lower() == "a" else "dom"
        self.province = args.province
        self.city = args.city
        self.offer = "wynajem" if args.offer == "rent" else "sprzedaz"
        self.distance = args.distance
        self.district = args.district if args.district else args.city
        self.data = list()

        # Build HTTP query
        base = "https://www.otodom.pl/pl/wyniki"
        self.url = f"{base}/{self.offer}/{self.type}/{self.province}"
        self.url += f"/{self.district}/{self.city}/{self.city}"
        self.url += f"?distanceRadius={self.distance}&limit=72"

        self.log = logging.getLogger(__name__)
        self.log.debug(f"Created url {self.url}")

        self.currentPage = 1
        self.maxPage = 1
        self._connector()
        self._formatData()


    def _getHeaders(self):
        """Generate headers with random user agent"""
        with open('useragents.txt', 'r') as f:
            ua = f.readlines()
        return {"User-Agent": ua[random.randint(0, len(ua)-1)].strip()}


    def _connector(self):
        """Making connection to given address"""
        self.log.debug(f"Starting connector {self.currentPage}")
        if self.currentPage <= self.maxPage:
            response = requests.get(f"{self.url}&page={self.currentPage}",
                                     headers=self._getHeaders()).content
            self._scrapper(response)
            self._connector()
        else:
            self._formatData()


    def _scrapper(self,html):
        """Grabbing offers from HTML"""
        self.log.debug(f"Scrapper got content length: {len(html)}")
        self.soup = BeautifulSoup(html, "html.parser")
        container = self.soup.select('article[data-cy="listing-item"]')
        self.log.warning(f"Found offers: {len(container)}")


        for element in container:
            id = 0 if len(self.data) == 0 else len(self.data)
            self.data.append({})
            # Grabbing rent and price
            priceBox = element.select('div[data-testid="listing-item-header"] > span')[0].text
            priceBox = re.split("\d*zł\+ czynsz:", priceBox)
            if len(priceBox) != 2: 
                price = 0
                rent = 0
                total = float(priceBox[0].replace('zł', '').replace(',','.')[:-1])
            else:
                price = float(re.sub('\\xa0', '', priceBox[0]).strip().replace(',','.'))
                rent = float(re.split("\\xa0", priceBox[1])[0].replace(',','.').strip())
                total = price + rent
            self.data[id]['price'] = price
            self.data[id]['rent'] = rent
            self.data[id]['total'] = total

            # Grabbing other info
            titleBox = element.select('a[data-cy="listing-item-link"]')[0]
            self.data[id]['title'] = titleBox.select('p')[0].text
            self.data[id]['link'] = f"https://www.otodom.pl{titleBox['href']}"
            self.data[id]['address'] = element.select('p[data-testid="advert-card-address"]')[0].text
            infoBox = element.select('div[data-testid="advert-card-specs-list"] dl dd')
            self.data[id]['rooms'] = int(re.split("\d*pok",infoBox[0].text)[0])
            self.data[id]['size'] = float(re.split(" ", infoBox[1].text)[0])
            self.log.debug(f"Added offer {id}")

        # Grabbing total page
        try:
            total = self.soup.select('ul[data-testid="frontend.search.base-pagination.nexus-pagination"] li')
            self.maxPage = int(total[len(total)-2].text)
        except: total = self.currentPage
        self.currentPage += 1
        return self.currentPage


    def _formatData(self):
        self.log.info('Saving to csv file')
        with open("output.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            field = ["LP", "title", "address", "price", "rent", "total", "rooms", "size", "perM","link"]
            writer.writerow(field)
            for index,offer in enumerate(self.data):
                perM = round(offer['total']/offer['size'], 2)
                writer.writerow([
                    index, offer['title'], offer['address'], offer['price'],
                    offer['rent'], offer['total'], offer['rooms'], offer['size'],
                    perM, offer['link']])

