import time
import csv
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import random
import sqlite3

# declaration of user agent to avoid getting blacklisted again. Never again.
headers = {'user-agent' : 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30)'}

# open recipe page
mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
driver = webdriver.Chrome(chrome_options = chrome_options)
driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

with open('/Users/simonedebrowney/PycharmProjects/recipecrawler/csvfile-chickpeas.csv', 'r') as csvfile:
    readCSV = csv.reader(csvfile, delimiter='\n')
    for row in readCSV:
        try:
            url = ''.join(row)
            print(url)
            driver.get(url)

            # connect to a SQLite database file
            sqlite_file = '/Users/simonedebrowney/Documents/recipes/recipechickpea.db'
            conn = sqlite3.connect(sqlite_file)
            c = conn.cursor()

            #declare variables
            TITLE = None
            AUTHOR = None
            AUTHORURL = None
            RATING = 0
            INGREDIENTS = None
            DIRECTIONS = None

            # variable for checking if recipe has timeout
            recipetimeout = False

            # get the recipe id from the url
            recipeString = url
            stringList = recipeString.split("/")
            #print(stringList[4])
            RecipeID = stringList[4]
            #print(RecipeID)

            # check if recipeID exists
            c.execute('''SELECT RecipeID FROM RECIPE WHERE RecipeID = ?''', (RecipeID,))
            exists = c.fetchone()
            if exists is None:

                # uses beautifulsoup for parsing
                def getdata():
                    global TITLE, AUTHOR, AUTHORURL, INGREDIENTS, DIRECTIONS, RATING
                    source_code = requests.get(url)
                    plain_text = source_code.text
                    soup = BeautifulSoup(plain_text, "html.parser")
                    TITLE = soup.find('h1', {"class": "recipe-summary__h1"}).text
                    AUTHOR = soup.find('span', {"class": "submitter__name"}).text

                    for a in soup.findAll('div', {"class": "submitter__img"}):
                        for b in a.findAll('a'):
                            AUTHORURL = b.get('href')
                            #print(AUTHORURL)

                    for ingrlist in soup.find_all('span', {"itemprop": "ingredients"}):
                        INGREDIENTS = ingrlist.text
                        conn.execute('''INSERT INTO INGREDIENTS(
                                        INGREDIENT, RecipeID) VALUES (?, ?)''',
                             (INGREDIENTS, RecipeID))

                    DIRECTIONS = ""
                    for steps in soup.find_all('span', {"class": "recipe-directions__list--item"}):
                        DIRECTIONS = DIRECTIONS + " " + (steps.text)

                    #print(TITLE)
                    #print(AUTHOR)

                    # getting the rating
                    #print("Rating")
                    for tag in soup.find_all("meta"):
                        if(tag.get("property", None)=="og:rating"):
                            RATING = tag.get('content')
                            #print (RATING)

                    # randomize pace of scraping
                    # seconds = 5 + (random.random() * 5)
                    seconds = 3
                    time.sleep(seconds)


                # uses selenium for parsing
                getdata()

                NumMADE = driver.find_element_by_class_name('made-it-count').text
                #print(NumMADE)

                # save into database for recipes
                conn.execute('''INSERT INTO RECIPE(
                        RecipeID, TITLE, AUTHOR, AUTHORURL, RATING, DIRECTIONS, NumMADE) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (RecipeID, TITLE, AUTHOR, AUTHORURL, RATING, DIRECTIONS, NumMADE))

                # find reviews section
                driver.find_element_by_class_name('recipe-reviews')
                numReviews = driver.find_element_by_class_name('recipe-reviews__header--count')

                count = 0
                if(numReviews.text != '0' and numReviews.text != '1'):
                    # clicking "Read more" gives a pop-up that does not provide the full rating of review. Eliminate solution
                    # can't do a right click command because of MoveTargetOutOfBoundsException. Allrecipes is just too messy
                    # Solution: get link to comment and go to that link
                    allreviews = driver.find_element_by_link_text('Read more')
                    driver.get(allreviews.get_attribute('href'))

                    # keep on clicking more reviews until all reviews are exhausted
                    nextbtn = driver.find_element_by_link_text('Next review')

                    while nextbtn:
                        try:
                            # scrape all information needed

                            # get the userId of reviewer
                            author = driver.find_element_by_tag_name('h4')
                            #print(author.text)
                            RevUSERID = author.text
                            RevUSERURL = driver.find_element_by_xpath(
                            '//*[@id="review"]/div[2]/article/div[1]/a[2]').get_attribute('href')
                            # print(RevUSERURL)

                            # This is section to get all information from one review
                            # get to the review
                            driver.find_elements_by_class_name('review-container')

                            # get the rating of review
                            rating = driver.find_element_by_class_name('rating-stars')
                            RevRATING = rating.get_attribute('data-ratingstars')
                            #print(RevRATING)

                            # get number of followers of reviewer
                            followers = driver.find_element_by_class_name('cook-details__followers')
                            #print(followers.text)
                            RevFOLLOWERS = followers.text

                            # get number of favorites of reviewer
                            favorites = driver.find_element_by_class_name('cook-details__favorites')
                            #print(favorites.text)
                            RevFAVORITES = favorites.text

                            # get number of recipes made by reviewer
                            numRecipes = driver.find_element_by_class_name('cook-details__recipes-made')
                            #print(numRecipes.text)
                            RevRECIPES = numRecipes.text

                            # get full review
                            fullreview = driver.find_element_by_tag_name('p')
                            #print(fullreview.text)
                            RevREVIEW = fullreview.text

                            conn.execute('''INSERT INTO REVIEWS(RevUSERID, RevUSERURL, RevRATING, RevFOLLOWERS, RevFAVORITES, RevRECIPES,
                                                   RevREVIEW, RecipeID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                 (RevUSERID, RevUSERURL, RevRATING, RevFOLLOWERS, RevFAVORITES, RevRECIPES,
                                  RevREVIEW, RecipeID,))

                            count += 1
                            print(count)

                            # proceed to next page
                            driver.get(nextbtn.get_attribute('href'))
                            nextbtn = driver.find_element_by_link_text('Next review')

                        except Exception as e:
                            if (isinstance(e, TimeoutException)):
                                # want to skip the current recipe and rescrape when program runs again
                                print("Recipe skipped")
                                recipetimeout = True

                            print(e)
                            break           # without catching exception, it will attempt to keep on clicking read more even if it's not there
                else:
                    pass
                # close the connection and operations on the database file
                # check if recipe has timeout and if so do not commit changes
                if (recipetimeout == False ):
                    conn.commit()

                conn.close()
                print("Finished scraping recipe")

            else:
                print("Recipe already exists")
                conn.close()
                pass

        except TimeoutException:
            print("Recipe skipped")
            conn.close()
            pass

driver.quit()
csvfile.close()
quit()



