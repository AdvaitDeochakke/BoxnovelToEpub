import my_funcs as mf
from ebooklib import epub

book = epub.EpubBook()

start_time = mf.get_time()

page = "https://boxnovel.com/novel/outside-of-time/chapter-1/"

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

while next_chap is not None:# and counted<1:
    
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
    
    texts = soup.find_all("div", class_="dib pr")
    
    # type 1 chapters 
    
    if texts:
        title = soup.find("h1", class_="dib mb0 fw700 fs24 lh1.5").get_text()
        title = mf.fix_your_titles(title)
        filetitle = mf.windows_validate(title)
        chapter_text += (title)
        chapter_text += (u"</h1>")
        
        subtitle = soup.find("h2", class_="subtitle fw400")
        
        # if the translator kept the subtitle text
        
        if subtitle:
            subtitle = subtitle.get_text()
            chapter_text += (u"<h2>")
            chapter_text += (subtitle)
            chapter_text += (u"</h2>")
            if counted<1:
                author = subtitle
                book.add_author(author)
                
        chapter_text += (u"<br>")
        for text in texts:
            chapter_text += (str(text.find("p")))
            
    # type 2 chapters
    
    else:
        text_wrapper = soup.find("div", class_="text-left")
        texts = text_wrapper.find_all("p")

        # translator is extra lazy

        if texts[0].find("br"):
            texts[0].find("br").replaceWith("break_finder")
            flipper = str(texts[0].get_text())
            
            title = flipper.split("break_finder")[0]
            new_start = "<p>" + flipper.replace(title + "break_finder", "") + "</p>"
            texts.pop(0)
            texts.insert(0, new_start)
            
        else:
            title = texts[0].get_text()
            
        title = mf.fix_your_titles(title)
        filetitle = mf.windows_validate(title)
        chapter_text += (title)
        chapter_text += (u"</h1>")
        texts.pop(0)

        for text in texts:
            chapter_text += (str(text))

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