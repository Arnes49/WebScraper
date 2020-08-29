import imghdr
import os
import shutil
import smtplib
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup


def send_email(a_header, a_text, image_numbers):
    email_address = "email_address"
    email_password = "email_password"

    msg = EmailMessage()
    msg['Subject'] = a_header
    msg['From'] = email_address
    msg['To'] = 'youraddress'
    msg.set_content(a_text)

    # creating list with files' names
    files = []
    i = 0
    while i < image_numbers:
        files.append(str(i+1) + '.jpg')
        i += 1

    # reading files from directory and attach them to message
    for file in files:
        with open("photos\\" + file, 'rb') as f:
            file_data = f.read()
            file_type = imghdr.what(f.name)
        msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=f.name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)


domain = "http://tuke.sk"

main_page = requests.get("http://tuke.sk/wps/portal/tuke/university/news").text
soup = BeautifulSoup(main_page, 'lxml')

# scraping all articles from main page by one
for item in soup.find_all('article'):
    if os.path.isdir('photos'):
        pass
    else:
        os.mkdir('photos')

    article_link = item.h1.a.get('href')
    article_page = requests.get(domain + article_link).text
    article_soup = BeautifulSoup(article_page, 'lxml')

    content = article_soup.find('div', class_='detail')

    # store article's content in lists
    header = content.h1.text
    paragraphs = []
    images = []
    lists = []

    # scraping paragraphs
    for paragraph in content.find_all('p'):
        paragraphs.append(paragraph.text)

    # scraping images
    for image in content.find_all('p'):
        if image.img is not None:
            image_link = domain + image.img.get('src')
            images.append(image_link)

    index = 1
    # upload scraped images to folder
    for image in images:
        image_data = requests.get(image).content
        with open("photos\\" + str(index) + '.jpg', 'wb+') as photo:
            photo.write(image_data)
        index += 1

    # scraping list <ul>
    for ul in content.find_all('ul', class_='list-arrow'):
        lists.append(ul.text)

    # concatenate paragraphs altogether
    article_text = ""
    for paragraph in paragraphs:
        if len(paragraph) > 1:
            article_text += paragraph + '\n'

    # concatenate lists to paragraph
    if len(lists) > 0:
        for ul in lists:
            article_text += str(ul) + '\n'

    send_email(header, article_text, len(images))

    # remove directory with photos
    shutil.rmtree('photos')
