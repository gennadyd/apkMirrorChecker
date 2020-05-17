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
import os

# Set Logger dile and console

formatter = json_log_formatter.JSONFormatter()

logger = logging.getLogger(__name__)

jsonHandler = logging.FileHandler(filename='./log/appkChecker.log')
jsonHandler.setFormatter(formatter)
logger.addHandler(jsonHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

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
        # logger.info('getRSSItems', extra={'getRSSItems': getRSSItems})                
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
    """
    emailNotification: Send email notification if provided. Using mailjet api
    """
    logger.info('Send notification', extra={'toaddrs':toaddrs,'subject':subject, 'body':rssItems})

    api_key = ''
    api_secret = ''
   
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
            "From": {
                "Email": "email-notifier@gmail.com",
                "Name": "email-notifier"
            },
            "To": [
                {
                "Email": toaddrs,
                "Name": "recipient"
                }
            ],
            "Subject": subject,
            "HTMLPart": rssItems,
            "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    try:    
        result = mailjet.send.create(data=data)
        logger.info('emailNotification', extra={'result': result.json()})
        return result.json()
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
        if not rssItems:
            logger.info('No New Release Found')
        else:
            if parsed_args.notification:
                emailNotification (parsed_args.notification, "New Releases", rssItems)
    else : 
        logger.info('No New Release Found')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='please provide APK apkmirror url', default=os.environ['URL'])
    parser.add_argument('-i', '--interval', help='please set interval in seconds', default=os.environ['INTERVAL'])
    parser.add_argument('-n', '--notification', help='please provide email address', default=os.environ['NOTIFICATION'])
    args = parser.parse_args()    
    main(args)
