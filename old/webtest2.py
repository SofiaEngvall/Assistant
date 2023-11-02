from requests import get
import re
import urllib.request
from urllib.request import Request, urlopen
import webbrowser

url = "https://fixitnow.se"
url = "https://www.javatpoint.com/how-to-open-url-in-python"
headers = {'User-Agent': 'Mozilla/6.0'}
headers2 = {  # if problems, add more to the header
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',  # 'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'refere': 'https://example.com',
    # "Upgrade-Insecure-Requests": '1',
    'cookie': """your cookie value ( you can get that from your web page) """
}


def get_webpage(url):
    webpage = urlopen(Request(url, headers=headers),
                      timeout=10).read().decode('utf-8')
    print(webpage)


get_webpage(url)

exit()

# alternative
req = get(link)
result = req.text


# scrape example from noob
# import requests
# from bs4 import BeautifulSoup
# from urllib import urlopen

webpage = urllib.request.urlopen(
    'http://www.cmegroup.com/trading/products/#sortField=oi&sortAsc=false&venues=3&page=1&cleared=1&group=1').read()
findrows = re.compile('<tr class="- banding(?:On|Off)>(.*?)</tr>')
findlink = re.compile('<a href =">(.*)</a>')

row_array = re.findall(findrows, webpage)
links = re.finall(findlink, webpate)

print(len(row_array))

iterator = []
