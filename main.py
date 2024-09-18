import requests
import selectorlib
import smtplib
import os
import time
from threading import Thread
import sqlite3

if not os.path.exists("data.db"):
    with open("data.db", "w") as file:
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        cursor.execute("""
                       CREATE TABLE events (
                           Band TEXT, 
                           City TEXT, 
                           Date TEXT
                        )
                       """)
else:
    connection = sqlite3.connect("data.db")

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


def send_email(infos):
    password = os.getenv('PASSWORD')
    sender = "apptestbeno@gmail.com"
    receiver = "safwatsadiq14@gmail.com"
    
    Band, City, Date = [info.strip() for info in infos.split(',')] 
    
    message = f"""\
Subject: New Tour Alert
    
There is a new tour of {Band} in {City} at {Date}
"""
    
    gmail = smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(sender, password)
    gmail.sendmail(sender, receiver, message)
    gmail.quit()


def store(extracted):
    row = extracted.split(',')
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
    connection.commit()


def read(extracted):
    row = extracted.split(',')
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events where Band=? AND City=? AND Date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows
    


if __name__ == '__main__':
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            content = read(extracted)
            if not content:
                store(extracted)
                
                email_thread = Thread(target=send_email, args=(extracted,))
                email_thread.daemon = True
                email_thread.start()
        time.sleep(2)