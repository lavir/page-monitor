__author__ = 'ned'

import time
import hashlib
import requests
from urlparse import urlparse
from datetime import datetime
from models import Url, Page, session

def get_page(url):
  user_agent = {"User-agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
  full_path = urlparse(url)
  domain = full_path.netloc
  url_page = full_path.path
  downloaded_page = requests.get(url, headers=user_agent)
  downloaded_page_md5 = hashlib.md5(downloaded_page.content).hexdigest()
  stored_md5 = queryDB(url)

  if stored_md5 == 'page not found':
    #if we dont have the url in our db, create new url/page objects
    print '%s not found. Adding to database' %url
    url2db = Url(url=url)
    page2db = Page(page_md5=downloaded_page_md5, page_result=url2db)
    session.add(page2db)
    session.commit()
    write_page(downloaded_page.content, domain, url_page)
  elif downloaded_page_md5 == stored_md5[2]:
    #our page has not been updated, kick back and relax
    print '%s has not been updated. Exiting.' %url
  else:
    #our page has been updated, update the page_md5 entry in the page object
    print '%s has been updated. New md5 %s' %(url, downloaded_page_md5)
    url2db = session.query(Url).filter(Url.id == stored_md5[0]).one()
    page2db = Page(page_md5=downloaded_page_md5, page_result=url2db)
    session.commit()
    write_page(downloaded_page.content, domain, url_page)
  return

def write_page(download_page, domain, file):
  ts = datetime.strftime(datetime.utcnow(), '%Y-%m-%d_%H%M%S')
  if '/' in file:
    file = file.replace('/', '_')
    if file == '_':
      file = '%s_%s_index.html' %(ts, domain)
    else:
      file = '%s_%s_%s' %(ts, domain, file)
  outfile = open(file, 'w+')
  outfile.write(download_page)
  outfile.close()
  return

def queryDB(url):
  try:
    #return url.id, url, page_md5
    return (session.query(Url.id).filter(Url.url == url).first()[0], url, session.query(Page.page_md5).filter(Page.url_id == session.query(Url.id).filter(Url.url == url)).first()[0])
  except TypeError as error:
    return 'page not found'

def get_urls():
  urls = []
  with open('url.lst') as url:
    for u in url.readlines():
      urls.append(u.strip())
  return urls

def main():
  while True:
    for url in get_urls():
      get_page(url)
    time.sleep(180)

if __name__ == '__main__':
  main()