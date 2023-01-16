import requests
from bs4 import BeautifulSoup
import re
import os
from fnmatch import fnmatch

def fix_your_titles(title):
    print("in fix title: ", title)
    if not title.startswith("Chapter"):
        title = "Chapter " + title
        print(title)
        
    if ":" not in title:
        match = re.search(r"Chapter\s*(\d+)", title)
        if match:
            title = title.replace(match.group(0), match.group(0) + ":")
            print("after match : ", title)
    return title

def get_page(page):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(page, headers=headers)
    except requests.exceptions.ConnectionError as err:
        print("Connection Error : \n", err)
    except requests.exceptions.HTTPError as err:
        print("Http error : \n", err)
    return r

def get_soup(r):
    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as err:
        print("Error while parsing :\n", err)
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
