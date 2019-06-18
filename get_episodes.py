# -*- coding: utf-8 -*-
from time import sleep
import urllib.request, urllib.error, urllib.parse
import os
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

from .credentials import emailaddress, password
from bs4 import BeautifulSoup as BSoup

def inference_balises(tag):
    grandparent = tag.parent.parent
    parent_class = ['wpb_text_column', 'wpb_content_element', '']
    cond = (
        tag.has_attr('class') and tag['class'] == ['wpb_wrapper']
        and
        tag.parent.has_attr('class')
            and tag.parent['class'] == parent_class
        and grandparent.has_attr('class')
            and grandparent['class'] == ['wpb_wrapper']
            )
    if not cond: return False

    links =  tag.find_all('a')
    return len(links) == 2

def urls_title_from_tag(tag):
    atags = tag.find_all('a')
    refs = [a['href'] for a in atags]
    #get title
    title = None
    for atag in atags:
        if atag['href'].lower().endswith('mp3'):
            title = atag.text
            print('Parsing ok', title)
            break
    else:
        print('Parse issue for')
        print(tag.prettify())
    return refs, title

from selenium.webdriver.firefox.options import Options

headless = Options()
headless.add_argument("--headless")

print_pdfs_with_default_printer = False # Uses default printer on linux
target_subfolder = 'klimova'
quiet = True





class PodcastGetter(object):
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(20)

        if not os.path.exists(target_subfolder):
            os.makedirs(target_subfolder)
        os.chdir(target_subfolder)  # Use proper context manager instead
        self.present_files = [f for f in os.listdir('.')  if os.path.isfile(f)]
        print('init done')

    def log_in(self):
        print('logging in ', end=' ')
        import sys; sys.stdout.flush()
        driver = self.driver
        driver.get("https://russianpodcast.eu/russian-dacha-club")
        driver.find_element_by_name("email").send_keys(emailaddress)
        driver.find_element_by_name("password").send_keys(password)
        driver.find_element_by_name("LoginDAPLoginForm").click()
        print('logged in')

    def refreshed_page_source(self, delay=2):
        """ This is a heck because getting the content right after login
        gives you le login page content """
        driver = self.driver

        sleep(delay)
        driver.refresh() # The url is the same so you need to re-fetch the content
        print('refresed')
        sleep(0.5)
        source = driver.page_source
        return source

    def __call__(self):
        self.log_in()
        page_source = self.refreshed_page_source()
        print('got source')
        self.driver.quit()
        print('quitted driver')
        links_filenames = self.get_links_and_titles(
            source=page_source,
            finder_function=inference_balises
            )
        files_to_get = self.filter_files(links_filenames)
        self.process_files(files_to_get)



    @staticmethod
    def get_links_and_titles(source, finder_function):
        soup = BSoup(source, 'html.parser')
        items = soup.find_all(finder_function)
        return [urls_title_from_tag(m) for m in items]


    def filter_files(self, links_and_title):
        def filename(link):
            return link.split('/')[-1]
        def is_there(link_title):
            return filename(link_title) in self.present_files

        return [(link, filename(link), title)
                for links, title in links_and_title
                for link in links
                if not is_there(link)]


    def process_files(self, files_to_get):
        for link, filename, title in files_to_get:
            print('processing:\n', '\n'.join([link, filename, title]))
            with open(filename, 'wb') as f:
                f.write(urllib.request.urlopen(link).read())
                if filename.lower().endswith('pdf') and \
                        print_pdfs_with_default_printer:
                    print((os.system('lp %s' % filename)))


if __name__ == "__main__":
    try:
        print("Checking firefox driver is here")
        if quiet:
            driver = webdriver.Firefox(firefox_options=headless)
        else:
            driver = webdriver.Firefox()
    except Exception as E:
        import logging
        logging.exception(E)

        print("Looks like firefox webdriver is not installed")
        print("See https://github.com/mozilla/geckodriver/releases go to assets todownload")
        print("https://stackoverflow.com/questions/42204897/how-to-setup-selenium-python-environment-for-firefox for more help")
    else:
        print("Yey firefox driver seems installed")
        PodcastGetter(driver)()

