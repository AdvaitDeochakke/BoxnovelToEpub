import requests
from bs4 import BeautifulSoup
import re
import os
from fnmatch import fnmatch
import time
import sys

def fileExists(filePath):
    return os.path.exists(filePath)

def get_time():
    return time.time()

def fix_your_titles(title):
    if title.startswith('<p>') and title.endswith('</p>'):
        title = title[3:-4]
    
    title = re.sub(r"^\d+\s*", "", title)
    
    if not re.search(r"Chapter\s*(\d+)", title):
        title = "Chapter " + title
        
    if ":" not in title:
        match = re.search(r"Chapter\s*(\d+)", title)
        if match:
            title = title.replace(match.group(0), match.group(0) + ":")
    return title

def get_page(page):
    #print(page, "entered")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(page, headers=headers)
    except requests.exceptions.ConnectionError as err:
        print("Connection Error : \n", err)
        sys.exit()
    except requests.exceptions.HTTPError as err:
        print("Http error : \n", err)
        sys.exit()
    #print(r)
    return r

def get_soup(r):
    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as err:
        print("Error while parsing :\n", err)
        sys.exit()
    #print(soup.prettify())
    return soup

def download_and_return_image_path(page, myId):
    image_url, img_path = get_image_location(page, myId)
    download_image(image_url, img_path)
    
    return img_path

def get_image_location(page, myId):
    match = re.search(r"(.*?)\/chapter", page)
    feed_page = match.group(1)+"/feed/"
    
    r = get_page(feed_page)
    soup = get_soup(r)
    
    imageDiv = soup.find("div", class_="summary_image")
    novelImg = imageDiv.find("img")
    image_url = novelImg.get('data-src')
    img_path = "creationData/" + myId + "_cover.jpg"
    
    return image_url, img_path

def download_image(image_url, img_path):
    r = requests.get(image_url)
    
    with open(img_path, "wb") as file:
        file.write(r.content)

def get_chapter_file_names():
    chapter_file_names = []

    for file_name in os.listdir("creationData"):
        if fnmatch(file_name, "*.xhtml"):
            chapter_file_names.append(file_name)
            
    return chapter_file_names

def windows_validate(title):
    invalid_chars = [":", "*", "\"", "\\", "/", "<", ">", "|", "?"]
    for invalid_char in invalid_chars:
        title = title.replace(invalid_char, "-")
    return title

def get_data(page, id=False):
    match = re.search(r"novel\/(.*?)\/chapter", page)
    novel_name = match.group(1)
    # if the word "boxnovel" appears in novel_name
    # remove it using re.sub
    novel_name = re.sub(r"\b(bronovel)\b", "", novel_name)
    
    new_name = windows_validate(novel_name)
    if(not id):
        new_name = new_name.replace("-", " ")
    if(id):
        new_name = new_name.replace("-", "_")
        new_name = new_name + "_id"
    return new_name

def get_chapter_title_for_epub(title):
    match = re.search(r"creationData\/(.*?)\.xhtml", title)
    chapter_name = match.group(1)
    chapter_name = chapter_name.replace("-", ":", 1)
    return chapter_name

def sterilize(page, start_chapter):
    if not page.startswith("https://"):
        page = "https://" + page
    if not re.search(r"/chapter-\d+/$", page):
        page = page.rstrip("/") + f"/chapter-{start_chapter}/"
    if not re.search(rf"/chapter-{start_chapter}/", page):
        page = page.split('/chapter')[0] + f"/chapter-{start_chapter}/"
    return page

def sanitize_pagelink(pagelink):
    pattern = r'^(https://)?bronovel.com/novel/[a-z-/]*(/chapter-(\d)*(/)?)?$'
    if not re.match(pattern, pagelink):
        print("Sorry, invalid link, try again")
        print(pagelink)
        return ""
    else:
        pagelink = sterilize(pagelink, 1)
        response = requests.get(pagelink)
        soup = BeautifulSoup(response.content, 'html.parser')

        body_tag = soup.body
        if 'error404' in body_tag.get('class', []):
            print("The page returned a 404 error. Try again")
            return ""
        else:
            print("The page is accessible. Starting crawl")
            return pagelink