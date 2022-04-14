# -*- coding: utf-8 -*-
from time import sleep
import urllib.request, urllib.error, urllib.parse
import os
from pprint import pprint, pformat
import logging

from selenium import webdriver

from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

from credentials import emailaddress, password
from bs4 import BeautifulSoup as BSoup

logging.basicConfig(
    format="%(asctime)s %(name)s  %(levelname)s  %(funcName)s %(lineno)d %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def inference_balises(tag):
    grandparent = tag.parent.parent
    parent_class = ["wpb_text_column", "wpb_content_element", ""]
    cond = (
        tag.has_attr("class")
        and tag["class"] == ["wpb_wrapper"]
        and tag.parent.has_attr("class")
        and tag.parent["class"] == parent_class
        and grandparent.has_attr("class")
        and grandparent["class"] == ["wpb_wrapper"]
    )
    if not cond:
        return False

    links = tag.find_all("a")
    return len(links) == 2


def urls_title_from_tag(tag):
    atags = tag.find_all("a")
    refs = [a["href"] for a in atags]
    # get title
    title = None
    for atag in atags:
        if atag["href"].lower().endswith("mp3"):
            title = atag.text
            print("Parsing ok", title)
            break
    else:
        print("Parse issue for")
        print(tag.prettify())
    return refs, title


from selenium.webdriver.firefox.options import Options

headless = Options()
debug = True
if debug:
    headless.headless = False

print_pdfs_with_default_printer = False  # Uses default printer on linux
target_subfolder = "klimova"
quiet = True


class PodcastGetter(object):
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(20)

        if not os.path.exists(target_subfolder):
            os.makedirs(target_subfolder)
        os.chdir(target_subfolder)  # Use proper context manager instead
        self.present_files = [f for f in os.listdir(".") if os.path.isfile(f)]
        print("init done")

    def log_in(self):
        print("logging in ", end=" ")
        import sys

        sys.stdout.flush()
        driver = self.driver
        driver.get("https://russianpodcast.eu/russian-dacha-club")
        driver.find_element_by_name("email").send_keys(emailaddress)
        driver.find_element_by_name("password").send_keys(password)
        driver.find_element_by_name("LoginDAPLoginForm").click()
        print("logged in")

    def refreshed_page_source(self, delay=2):
        """This is a heck because getting the content right after login
        gives you le login page content"""
        driver = self.driver

        sleep(delay)
        driver.refresh()  # The url is the same so you need to re-fetch the content
        print("refresed")
        sleep(0.5)
        source = driver.page_source
        return source

    def get_main_post(self):

        return self.driver.find_element(By.CSS_SELECTOR, "section.post-content")

    def get_podacast_page_links_tags(self, main_post):
        return main_post.find_elements(
            By.CSS_SELECTOR, "div.wpb_text_column > div.wpb_wrapper > p>a"
        )

    def __call__(self):
        self.log_in()
        page_source = self.refreshed_page_source()
        logger.info("got source")
        # self.wait(By.CSS_SELECTOR, 'section.post-content')
        main_post = self.get_main_post()

        page_links_tags = self.get_podacast_page_links_tags(main_post)
        urls = [tag.get_attribute("href") for tag in page_links_tags]
        logger.info(f"{len(urls)} tags found")

        # links_filenames = self.get_links_and_titles(finder_function=inference_balises)
        podcast_list = []
        for url in urls:  # go to page and fetch the postcast
            targets_podcat = "podcast" in url
            self.driver.get(url)
            link = self.driver.find_element(By.CSS_SELECTOR, "div.wpb_wrapper .fa")
            # [x.text for x in self.driver.find_elements(By.CSS_SELECTOR, "div.wpb_wrapper .fa+a").find_element(By.XPATH, '../').find_element(By.TAG, 'a')
            # https://developer.mozilla.org/fr/docs/Web/CSS/Adjacent_sibling_combinator
            link_tags = self.driver.find_elements(
                By.CSS_SELECTOR, "div.wpb_wrapper .fa+a"
            )
            logger.info(f"{len(link_tags)} found, expected 2")

            def parse_desc(s):
                stripped = s.split(">>")[-1].strip("' ").replace(" ", "_")
                return stripped

            for tag in link_tags:
                url = tag.get_attribute("href")
                title = parse_desc(tag.text)

                podcast_list.append((url, title))
                logger.info(f"Found {title} {url}")

        files_to_get = self.filter_files(podcast_list)
        logger.info(pformat(files_to_get))
        self.process_files(files_to_get)

        self.driver.quit()

    def filter_files(self, links_and_title):
        def is_there(title):
            return title in self.present_files

        return [
            (link, title, title)
            for link, title in links_and_title
            if not is_there(title)
        ]

    def process_files(self, files_to_get):
        if not files_to_get:
            logger.info("Nohing to download")
        for link, filename, title in files_to_get:
            print(f"processing: {title}")
            with open(filename, "wb") as f:
                f.write(urllib.request.urlopen(link).read())
                # if filename.lower().endswith("pdf") and print_pdfs_with_default_printer:
                #    print((os.system("lp %s" % filename)))


if __name__ == "__main__":
    try:
        print("Checking firefox driver is here")
        if quiet:
            driver = webdriver.Firefox(options=headless)
        else:
            driver = webdriver.Firefox()
    except Exception as E:
        import logging

        logging.exception(E)

        print("Looks like firefox webdriver is not installed")
        print(
            "See https://github.com/mozilla/geckodriver/releases go to assets todownload"
        )
        print(
            "https://stackoverflow.com/questions/42204897/how-to-setup-selenium-python-environment-for-firefox for more help"
        )
    else:
        print("Yey firefox driver seems installed")
        fetcher = PodcastGetter(driver)
        try:
            fetcher()
        except Exception:
            fetcher.driver.quit()
            raise
