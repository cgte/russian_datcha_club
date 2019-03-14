# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

from credentials import emailaddress, password
from bs4 import BeautifulSoup as BSoup

def inference_balises(tag):
    grandparent = tag.parent.parent
    parent_class = [u'wpb_text_column', u'wpb_content_element', u'']
    cond = (
        tag.has_attr('class') and tag['class'] == [u'wpb_wrapper']
        and
        tag.parent.has_attr('class')
            and tag.parent['class'] == parent_class
        and grandparent.has_attr('class')
            and grandparent['class'] == [u'wpb_wrapper']
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
            print 'Parsing ok', title
            break
    else:
        print 'Parse issue for'
        print tag.prettify()
    return refs, title

from selenium.webdriver.firefox.options import Options

headless = Options()
headless.add_argument("--headless")

print_pdfs_with_default_printer = False # Uses default printer on linux
target_subfolder = 'klimova'
quiet = False

class PodcastGetter(unittest.TestCase):
    def setUp(self):
        if quiet:
            self.driver = webdriver.Firefox(firefox_options=headless)
        else:
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://russianpodcast.eu"
        self.verificationErrors = []
        self.accept_next_alert = False

    def test_je_me_connecte(self):
        driver = self.driver
        driver.get("https://russianpodcast.eu/russian-dacha-club")
        driver.find_element_by_name("email").click()
        driver.find_element_by_name("email").clear()
        driver.find_element_by_name("email").send_keys(emailaddress)
        driver.find_element_by_name("password").click()
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(password)
        driver.find_element_by_name("LoginDAPLoginForm").click()
        from time import sleep
        sleep(2)
        driver.refresh() # The url is the same so you need to re-fetch the content
        klass = 'wpb_text_column wpb_content_element '

        soup = BSoup(driver.page_source, 'html.parser')
        megatop =  soup.find_all(inference_balises)
        self.driver.quit()
        print(len(megatop))
        to_fetch = []
        for m in megatop:
            res = urls_title_from_tag(m)
            to_fetch.append(res)
        import urllib2
        import os
        if not os.path.exists(target_subfolder):
            os.makedirs(target_subfolder)
        os.chdir(target_subfolder)
        present_files = [f for f in os.listdir('.')
                if os.path.isfile(f)]
        downloaded = []
        for links, title in to_fetch:
            for link in links:
                filename = link.split('/')[-1]
                if filename not in present_files:
                    with open(filename, 'wb') as f:
                        f.write(urllib2.urlopen(link).read())
                        downloaded.append(title)
                    if filename.lower().endswith('pdf'):
                        if print_pdfs_with_default_printer:
                            print(os.system('lp %s' % filename))
            print title
            print links
            print '---'
        print('Downloaded files')
        for title in downloaded:
            print(title)

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    try:
        print "Checking firefox driver is here"
        driver = webdriver.Firefox(firefox_options=headless)
        driver.quit()
    except Exception as E:
        import logging
        logging.exception(E)

        print "Looks like firefox webdriver is not installed"
        print "See https://github.com/mozilla/geckodriver/releases go to assets todownload"
        print "https://stackoverflow.com/questions/42204897/how-to-setup-selenium-python-environment-for-firefox for more help"
    else:
        print "Yey firefox driver seems installed"
        unittest.main()

