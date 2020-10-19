from bs4 import BeautifulSoup
import datetime
import csv

html = open("bookmarks.html").read()

soup = BeautifulSoup(html)

def getFiletime(dtms):
    return (datetime.datetime.fromtimestamp(dtms) - datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')

data = []    

for a in soup.find_all(href=True):
    print("Bookmark: ", a.string)
    print("URL: ", a['href'])
    print("Date: ", getFiletime(int(a['add_date'])))
    data.append([a.string,a['href'],getFiletime(int(a['add_date']))])

print(data)  
with open('bookmarks.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)
