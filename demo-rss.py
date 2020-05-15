from datetime import timedelta, timezone,datetime
import feedparser
from bs4 import BeautifulSoup
import unicodedata
import requests
import re
from mailjet_rest import Client
import logging
import json_log_formatter
import argparse

# Global
formatter = json_log_formatter.JSONFormatter()
json_handler = logging.FileHandler(filename='./demo-rss.json')
json_handler.setFormatter(formatter)
logger = logging.getLogger('demo-rss-logger')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)


def getLastRSSUpdate(url,rss_timestamp):
    """
        getLastRSSUpdate: Get the RSS feed lastBuildTime field 
    """ 
    NewsFeed = feedparser.parse(url)
    pageLastUpdated = (NewsFeed["channel"]["updated"])
    pageLastUpdatedTime =  datetime.strptime(pageLastUpdated, rss_timestamp)
    # print ("Last updated time of the RSS feed update time =", pageLastUpdatedTime)
    return pageLastUpdatedTime.replace(tzinfo=None)

def getRSSItems(url,rss_timestamp,currentTime,interval):
    """
      getRSSItems: Get list of versions that were published for a given period of time
    """ 
    try:    
        NewsFeed = feedparser.parse(url)
        entries = NewsFeed.entries
        newItems = {}
        for entry in entries: 
            publishedTime = datetime.strptime(entry.published, rss_timestamp).replace(tzinfo=None)
            deltaTimeRSS = (currentTime - publishedTime).total_seconds()
            if int(deltaTimeRSS) < interval :
                # print (entry.title,deltaTimeRSS,interval)
                release = "none"
                release_url = re.search(r'href=[\'"]?([^\'" >]+)', entry.content[0]["value"])
                if release_url:
                    release = getReleaseNotes(release_url.group(1))
                    print("New Version %s published %s " % (entry.title,publishedTime))

                # print(entry.title, entry.published, release)
                newItems[entry.title] = {"published": entry.published, "release_notes":release}
        return newItems
    except Exception as e:
        logger.info('getRSSItems', extra={'exception': e})      
        return e

def getReleaseNotes(url):
  """
    getReleaseNotes: Get release version 
  """
  try:
    session = requests.Session()
    headers = {'User-Agent': 'APKMirrorDemo/1.0'}
    session.headers.update(headers)
   
    resp    = session.get(url)
    html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')

    dom         = BeautifulSoup(html, 'html5lib')
    contentArea = dom.findAll('div', {'class': 'tab-content'})[0]
    for whatsnew in contentArea.findAll('div', {'id': 'whatsnew'}):
     for row in whatsnew.findAll('div', {'class': 'row'}):
      for notes in row.findAll('div', {'class': 'notes'}):
        return (notes.get_text())
   
  except Exception as e:
    logger.info('getReleaseNotes', extra={'exception': e})      
    return e

def emailNotification(toaddrs,subject, rssItems):
    logger.info('Send notification', extra={'toaddrs':toaddrs,'subject':subject, 'body':rssItems})

    api_key = 'acc533791a5144b415bfa022e9f3285f'
    api_secret = '0df4eb9eb8ef5e58c51f538c8720d9e7'
   
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
            "From": {
                "Email": "tdawnpbmbzbyrkrowi@ttirv.org",
                "Name": "email-notifier"
            },
            "To": [
                {
                "Email": "recipient@gmail.com",
                "Name": "recipient"
                }
            ],
            "Subject": "subject",
            "TextPart": "My first Mailjet emai",
            "HTMLPart": "<h3>Dear passenger 1, welcome to <a href='https://www.mailjet.com/'>Mailjet</a>!</h3><br />May the delivery force be with you!",
            "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    try:    
        # result = mailjet.send.create(data=data)
        # # print (result.content)
        # return result.json()
        return "Sent"
    except Exception as e:
        logger.info('emailNotification', extra={'exception': e})      
        return e

def main(parsed_args):


    logger.info('arguments', extra={'arguments': parsed_args})


    interval = int(parsed_args.interval)
    rss_timestamp = "%a, %d %b %Y %H:%M:%S %z"
    rss_url = parsed_args.url+"/feed"
    
    currentTime =  datetime.now()
    pageLastUpdatedTime = getLastRSSUpdate(rss_url,rss_timestamp)
    deltaTime = (currentTime - pageLastUpdatedTime).total_seconds()
    logger.info('times', extra={'currentTime': str(currentTime), "pageLastUpdatedTime": str(pageLastUpdatedTime), "deltaTime": deltaTime})
    if int(deltaTime) < interval :
        rssItems = getRSSItems(rss_url,rss_timestamp,currentTime,interval)
        logger.info('rssItems', extra=rssItems)
        if parsed_args.notification:
            emailNotification (parsed_args.notification, "New Releases", rssItems)
    else : 
        logger.info('No New Release Found')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='please provide APK apkmirror url', default="https://www.apkmirror.com/apk/supercell/brawl-stars/")
    parser.add_argument('-i', '--interval', help='please set interval in seconds', default=7200)
    parser.add_argument('-n', '--notification', help='please provide email address', default=None)
    args = parser.parse_args()    
    main(args)
