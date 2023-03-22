import my_funcs as mf
from ebooklib import epub
import re
import sys

book = epub.EpubBook()

start_time = mf.get_time()

print("Give the link to the novel, can be novel page, or any chapter page")
pagelink = ""
pagelink = input()

pagelink = mf.sanitize_pagelink(pagelink)
if pagelink == "":
    sys.exit()

page = pagelink
print("Enter the start and end chapters")
print("enter -1 if you want the full novel")
print("if you want the full novel from a certain chapter (say 100), enter \"100\" followed by a \"-1\"")
print("if you want a subset, enter \"100\" \"146\"")

start_chapter = 0
end_chapter = 0

while True:
    try:
        start_chapter = input()
        if int(start_chapter) < 0:
            start_chapter = 0
            end_chapter = 0
            print("sure, getting full novel")
        else:
            end_chapter = input()
            if int(end_chapter) < 0:
                end_chapter = 0
                print("getting full novel from chapter", start_chapter)
            else:
                print("getting novel from chapter ", start_chapter, "to", end_chapter)
        
        start_chapter = int(start_chapter)
        end_chapter = int(end_chapter)
        break
        
    except ValueError:
        print("invalid numbers entered. please enter a NUMBER. try again")
        
whetherFull = False
if end_chapter == 0:
    whetherFull = True
needed_chapters = int(end_chapter) - int(start_chapter) +1
page = mf.sterilize(page, start_chapter)

myTitle = mf.get_data(page)
print("got title - ", myTitle.title())
myId = mf.get_data(page, id=True)
author = ""

myImage = mf.download_and_return_image_path(page, myId)
print("got cover image")

image_content = open(myImage, 'rb').read()
cover_img = epub.EpubImage(uid='cover_img', file_name=myImage, media_type='image/gif', content=image_content)    
book.set_cover(myImage, content=image_content)


book.set_identifier(myId)
book.set_title(myTitle.title())
book.set_language("en")

book.spine = ['nav']

next_chap = "not none"
counted = 0

#to-do : i figured out the text-left thing is everywhere, need to do that now
#need to rewrite the code so that the logic flow is 
#retrieve page
#check if any title identifiers are present (cha-tit, dib mb0, etc)
#if yes, proceed accordingly
#then go through the rest of the page, taking the text from the <p>s

while next_chap is not None and (counted<needed_chapters or whetherFull):
    
    chapter_text = ""
   
    # epub chapters are html
    chapter_text += (u"<html><head></head><body><h1>")
    
    # This code block is used to navigate to the next chapter on 
    # the webpage specified by the 'page' variable.

    r = mf.get_page(page)
    soup = mf.get_soup(r)

    # getting the next chapter link
    
    next_chap = soup.find("div", class_ = "nav-next")
    if next_chap is not None:
        page = next_chap.find("a")["href"] # making sure the page variable is changed for iteration
    
    # Retrieving and formatting chapter title and subtitle, 
    # appending to the chapter_text list
    
    texts = soup.find("div", class_="text-left")
    h1_element = texts.find('h1')
    h2_element = texts.find('h2')
    h3_element = texts.find('h3')
    incorrect_title = 1 # set false if there is a clear h1/h2/h3 around title
    # otherwise, high possibility that erroneous formatting
    if h1_element:
        cur_element = h1_element
        incorrect_title = 0
    elif h3_element and not h1_element:
        cur_element = h3_element
        incorrect_title = 0
    elif h2_element and not (h1_element or h3_element):
        cur_element = h2_element
        incorrect_title = 0
    else:
        cur_element = texts.find('p')
        # if the text inside the cur_element contains 
        # a regex pattern as such
        # the word chapter, followed by a space or hypen, followed by a number
        # set 'incorrect_title' to 0 (its not incorrect, just pure lazy)
        if re.search(r'chapter[-\s]\d+', cur_element.text, re.IGNORECASE):
            incorrect_title = 0
    
    if re.search(r"<br />", str(cur_element)) or re.search(r"<br/>", str(cur_element)):
        if re.search(r"<br />", str(cur_element)):
            title_element = (str(cur_element).split("<br />")[0]).split("<p>")[1]
            rest_element = "<p>" + str(cur_element).split("<br />")[1]
        else:
            title_element = (str(cur_element).split("<br/>")[0]).split("<p>")[1]
            rest_element = "<p>" + str(cur_element).split("<br/>")[1]
            
        title = mf.fix_your_titles(title_element)
        filetitle = mf.windows_validate(title)
        chapter_text += title
        chapter_text += (u"</h1><br>")
        chapter_text += rest_element

    # there are a few chapters where the <p> tag is just not opened for title?
    # that causes issues at times and I have no clue how to fix it without breaking more things
    # pretty cope fix is breaking if len > some number
    
    elif (len(str(cur_element)) > 100 and incorrect_title): # dont want to break longer but correct titles
        # check if length of str(cur_element) > 100
        # if yes, break it at the last space just under 100
        # title_element = first part
        # rest_element = "<p>" + remaining part
        index = str(cur_element)[:100].rfind(' ')
        title_element = str(cur_element)[:index]
        rest_element = "<p>" + str(cur_element)[index+1:]

        title = mf.fix_your_titles(title_element)
        filetitle = mf.windows_validate(title)
        chapter_text += title
        chapter_text += (u"</h1><br>")
        chapter_text += rest_element
    
    else:
        title = mf.fix_your_titles(cur_element.get_text())
        filetitle = mf.windows_validate(title)
        chapter_text += (title)
        chapter_text += (u"</h1><br>")
        
    # Another issue is some chapters are completely hosted on the website and instead have a 
    # link to another text hosting site
    # i dont really wannt work around that tbh
        
    # Another issue is that some novels have multiple chapters hosted on the same page
    # that makes it so that the link is something like /chapter-1-10/
    # i CAN solve it if i figure out a way to get the link from the dropdown linklist and iterate
    # but honestly, cba
    
    if h2_element and (h1_element or h3_element):
        cur_element = h2_element
        subtitle = cur_element.get_text()
        chapter_text += (u"<h2>")
        chapter_text += (subtitle)
        chapter_text += (u"</h2>")
        chapter_text += (u"<br>")
        if counted<1:
            author = subtitle
            book.add_author(author)
    
    all_p = texts.find_all('p')
    for tag_p in all_p[1:]:
        chapter_text += (str(tag_p))

    chapter_text += (u"</body></html>")
    
    # write to file, check if exists, update progress
    chapter = epub.EpubHtml(title= title, 
                                file_name=filetitle+'.xhtml', lang='en')
    chapter.content = chapter_text
    book.add_item(chapter)
    book.toc.append(epub.Link(filetitle+'.xhtml', title, 'chapter'))
    book.spine.append(chapter)
    print("Added ", title, " to epub")
    counted+=1

ttl_time = mf.get_time() - start_time
avg_time = ttl_time/counted

print("\ntook total time of ", ttl_time, " to finish", sep="")
print("\navg time per chapter is around ", avg_time, sep="")

# Add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

print("writing epub")
epub.write_epub(myTitle.title() + ".epub", book, {})

print("done. File is found in current directory as ", myTitle, ".epub", sep="")