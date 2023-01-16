import my_funcs as mf  

page = "https://boxnovel.com/novel/outside-of-time/chapter-1/"

myTitle = mf.get_data(page)
print("got title - ", myTitle.title())
myId = mf.get_data(page, id=True)
author = ""
myImage = mf.download_and_return_image_path(page, myId)
print("got cover image")

next_chap = "not none"
counted = 0

while next_chap is not None:# and counted<1:
    
    chapter_text = []
   
    # epub chapters are html
    chapter_text.append(u"<html><head></head><body><h1>")
    
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
        chapter_text.append(title)
        chapter_text.append(u"</h1>")
        
        subtitle = soup.find("h2", class_="subtitle fw400")
        
        # if the translator kept the subtitle text
        
        if subtitle:
            subtitle = subtitle.get_text()
            chapter_text.append(u"<h2>")
            chapter_text.append(subtitle)
            chapter_text.append(u"</h2>")
            if counted<1:
                author = subtitle
                
        chapter_text.append(u"<br>")
        for text in texts:
            chapter_text.append(text.find("p"))
            
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
        chapter_text.append(title)
        chapter_text.append(u"</h1>")
        texts.pop(0)

        for text in texts:
            chapter_text.append(text)

    chapter_text.append(u"</body></html>")
    
    # write to file
    
    with open("creationData/{}.xhtml".format(filetitle), "w", encoding='utf8') as file:
       for line in chapter_text:
           file.write(str(line) + "\n")
    
    # testing stuff, ignore this and below comment
    #counted+=1
    
    # Progress update
    print("got ", title)

#-----------------------------------------------------------------------------------------------

# calling ebooklib to convert to epub

from ebooklib import epub
book = epub.EpubBook()

# metadata setting

book.set_identifier(myId)
book.set_title(myTitle.title())
book.set_language("en")

book.add_author(author)

book.spine = ['nav']

# Add chapters to the book

chapter_file_names = mf.get_chapter_file_names()

for file_name in chapter_file_names:
    true_file_name = "creationData/{}".format(file_name)
    
    with open(true_file_name, "r", encoding='utf8') as file:
        chapter_text = file.read()
        chap_title = mf.get_chapter_title_for_epub(true_file_name)
        chapter = epub.EpubHtml(title= chap_title, 
                                file_name=file_name, lang='en')
        chapter.content = chapter_text
        book.add_item(chapter)
        book.spine.append(chapter)
        
print("creating toc")

# Add to the ToC

for chapter_file_name in chapter_file_names:
    book.toc.append(epub.Link(chapter_file_name, mf.get_chapter_title_for_epub(chapter_file_name), 'chapter'))
    
# Add cover art
image_content = open(myImage, 'rb').read()
cover_img = epub.EpubImage(uid='image_1', file_name=myImage, media_type='image/gif', content=image_content)    
book.set_cover(myImage, content=image_content)

# Add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

print("writing epub")
epub.write_epub(myTitle.title() + ".epub", book, {})

print("done. File is found in current directory as ", myTitle, ".epub", sep="")