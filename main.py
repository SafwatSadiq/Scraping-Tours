import requests
import selectorlib
import smtplib
import os
import time
from threading import Thread

if not os.path.exists("data.txt"):
    with open("data.txt", "w") as file:
        pass


URL = 'https://programmer100.pythonanywhere.com/tours/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}



def scrape(url):
    """Scrape the page source from the url"""
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)['tours']
    return value


def send_email(info):
    password = os.getenv('PASSWORD')
    sender = "apptestbeno@gmail.com"
    receiver = "safwatsadiq14@gmail.com"
    
    message = f"""\
Subject: New Tour Alert
    
{info}
"""
    
    gmail = smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(sender, password)
    gmail.sendmail(sender, receiver, message)
    gmail.quit()


def store(extracted):
    with open("data.txt", "a") as file:
        file.write(extracted + "\n")


def read():
    with open("data.txt", "r") as file:
        return file.read()


if __name__ == '__main__':
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        content = read()
        if extracted != "No upcoming tours":
            if not extracted in content:
                store(extracted)
                
                email_thread = Thread(target=send_email, args=(extracted,))
                email_thread.daemon = True
                email_thread.start()
        time.sleep(2)