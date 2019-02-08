from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
import requests
import re


def scrape():
        ########################################
        ########### NASA Mars News #############
        ########################################
        url = 'https://mars.nasa.gov/news/'

        # get response from url
        response = requests.get(url)

        # Create BeautifulSoup object; parse with 'html'
        soup = bs(response.text, 'html.parser')

        # scraped news title and paragraph
        news_title = soup.find('div', class_='content_title').a.text
        news_p = soup.find('div', class_='rollover_description_inner').text


        ########################################
        ######## JPL Mars Space Images #########
        ########################################

        # start up browser
        executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
        browser = Browser('chrome', **executable_path, headless=False)

        # URL and sub-url to concatenate image_url to end of it
        url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        sub_url = 'https://www.jpl.nasa.gov'

        # visit site
        browser.visit(url)


        html = browser.html
        soup = bs(html, 'html.parser')

        img_url = soup.find('div', class_='carousel_items').article['style']

        # strip image_url of unnecessary text
        strip_img_url = re.findall("\'(.*?)\'", img_url)
        # for some reason re.findall returns list, grab first element
        # to get final_img_url
        final_img_url = strip_img_url[0]

        # scraped image url
        featured_img_url = sub_url + final_img_url


        ########################################
        ######## Twitter Mars Weather #########
        ########################################
        twt_url = 'https://twitter.com/marswxreport?lang=en'

        # get response and create BeautifulSoup obj
        response = requests.get(twt_url)
        soup = bs(response.text, 'html.parser')

        # Get list of tweets
        tweet_list = soup.find_all("li", class_="js-stream-item")
        # Search through list for weather tweet
        for tweet in tweet_list:
            if tweet.div["data-screen-name"] == "MarsWxReport":
                mars_weather = tweet.find('p', class_="tweet-text").text

        ########################################
        ############# Mars Facts ##############
        ########################################

        facts_url = 'http://space-facts.com/mars/'


        tables = pd.read_html(facts_url)

        df = tables[0]
        html_table = df.to_html()

        ########################################
        ########### Mars Hemispheres ###########
        ########################################

        hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

        # Get response and create bs object
        response = requests.get(hemi_url)
        soup = bs(response.text, 'html.parser')

        # looking at all relevant posts
        results = soup.find_all('div', class_='description')

        # Create list of hemisphere names for partial match ids
        hemispheres = ['Cerberus', 'Schiaparelli', 'Syrtis', 'Valles']

        # empty list where dictionary posts will go
        hemisphere_image_urls = []

        # Visit actual website
        browser.visit(hemi_url)
        # iterator, couldn't get iterable from all variables made
        i = 0

        for result in results:
                # click hemisphere link
                browser.click_link_by_partial_text(hemispheres[i])

                # get current browser url and make bs obj
                html = browser.html
                soup = bs(html, 'html.parser')

                # find title and image url, post to dictionary
                title = soup.find('h2', class_='title').text
                img_url = soup.find('a', target='_blank')['href']
                post = {
                        'title': title,
                        'img_url': img_url
                        }
                # append to empty list
                hemisphere_image_urls.append(post)
                
                # increment iterable and go back one page
                i += 1
                browser.back()
        
        browser.quit()

        scrape_items = {
                'news_title': news_title,
                'news_p': news_p,
                'featured_img_url': featured_img_url,
                'mars_weather': mars_weather,
                'mars_facts': html_table,
                'hemisphere_image_urls': hemisphere_image_urls
        }

        return scrape_items
