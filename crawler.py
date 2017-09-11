import requests
from bs4 import BeautifulSoup
import time
import csv

# declaration of user agent to avoid getting blacklisted again. Never again.
headers = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36)'}

# function to find links to just recipes
def recipe_spider(max_pages):
    page = 1

    while page <= max_pages:
        url = "http://allrecipes.com/search/results/?wt=lentils&sort=re&page=" + str(page)
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "html.parser")

        partialSet = set()
        for link in soup.find_all('a', {"data-internal-referrer-link": "hub recipe"}):
            href = link.get('href')

            # href will output links that are videos, recipes, and user profiles
            if "recipe" in href: # to ensure we only get recipes
                fullLink = "http://allrecipes.com" + href
                partialSet.add(fullLink)
        page += 1   # increment page number
        time.sleep(5)  # wait 10 seconds before we make the next request

        with open('csvfile.csv', 'a') as file:
            for item in partialSet:
                file.write(item)
                file.write('\n')
                # print(item)


# Instructions: input needs to be the number of pages you would like to search
recipe_spider(15)
print("Process completed")

