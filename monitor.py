__author__ = 'ned'

import os
import time
import hashlib
import requests
from urlparse import urlparse
from datetime import datetime
from models import Url, Page, session

CWD = os.getcwd()

def get_page(url):
  user_agent = {"User-agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
  full_path = urlparse(url)
  domain = full_path.netloc
  url_page = full_path.path
  if url_page == '':
    url_page = 'index.html'
  try:
    downloaded_page = requests.get(url, headers=user_agent)
    downloaded_page_md5 = hashlib.md5(downloaded_page.content).hexdigest()
  except requests.exceptions.ConnectionError as error:
    print '%s is unavailable. %s received' %(url, error)
    return

  stored_md5 = queryDB(url)

  url2db = stored_md5[0]
  page_md5 = stored_md5[2]
  if stored_md5 == 'page not found' or stored_md5[0] == None:
    #if we dont have the url in our db, create new url/page objects
    print '%s not found. Adding to database' %url
    checkdir, filename = write_page(downloaded_page.content, domain, url_page)
    dirpath = '%s/%s' %(checkdir, filename)
    url2db = Url(url=url)
    page2db = Page(page_md5=downloaded_page_md5, filename=dirpath, page_result=url2db)
    session.add(page2db)
    session.commit()
  elif downloaded_page_md5 == page_md5.page_md5:
    #our page has not been updated, kick back and relax
    print '%s has not been updated. Exiting.' %url
  else:
    #our page has been updated, update the page_md5 entry in the page object
    print '%s has been updated. New md5 %s' %(url, downloaded_page_md5)
    checkdir, filename = write_page(downloaded_page.content, domain, url_page)
    dirpath = '%s/%s' %(checkdir, filename)
    page2db = Page(page_md5=downloaded_page_md5, filename=dirpath, page_result=url2db)
    session.commit()
  return

def write_page(download_page, domain, file):
  ts = datetime.strftime(datetime.utcnow(), '%Y-%m-%d_%H%M%S')
  if '/' in file:
    filename = file.replace('/', '_')
    if filename == '_':
      filename = '%s_%s_index.html' %(ts, domain)
    else:
      filename = '%s_%s_%s' %(ts, domain, filename)
  else:
    filename = 'index.html'
  if filename[-1:] == '_':
    filename = filename[:-1]
  checkdir = '%s/%s' %(CWD, domain)
  if os.path.isdir(checkdir) is False:
    os.mkdir(checkdir)
  os.chdir(checkdir)
  outfile = open(filename, 'w+')
  outfile.write(download_page)
  outfile.close()
  return checkdir, filename

def queryDB(url):
  try:
    #return url.id, url, page_md5
    return (session.query(Url).filter(Url.url == url).first(), url, session.query(Page).filter(Page.url_id == session.query(Url.id).filter(Url.url == url)).first())
  except TypeError as error:
    return 'page not found'

def get_urls():
  urls = []
  os.chdir(CWD)
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