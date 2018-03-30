#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# tested with python 3.3.2

#import httplib,urllib
from html.parser import HTMLParser
import requests
import os,re,time,sys,json
import logging
import mimetypes

from Anzeige import Anzeige
from DDHtmlParser import DDHtmlParser

import http.client as http_client
http_client.HTTPConnection.debuglevel = 0
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = False
mimetypes.init()

configfile='.config.json'
config={}

def readConfig():
  return json.load(open(configfile))["dd"]

def login():
  session = requests.Session() 

  # login
  url=config['baseurl']+'/member_login.php'
  params = {'redirect_to': '', 'username': config['username'], 'password': config['password'], 'submit':'Einloggen'}
  response = session.post(url, data=params)
  response.raise_for_status() # -> make sure it is 200

  # page after login
  response = session.get(config['baseurl']+'/member.php')
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()
  #print(json.dumps(data,sort_keys=True,indent=4))

  return session

def getKeyByValue(dict,regexp):
  for key,value in dict.items():
    match=re.match(regexp,value)
    if match:
      return key

def get_next_delete_url(session):

  response = session.get(config['baseurl']+'/member.php')
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()

  try:
    response = session.get(config['baseurl']+'/'+data['links']['Anzeige(n) bearbeiten'])
  except Exception:
    print(print(json.dumps(data['links'],indent=4)))
    raise
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()
  #print(html)

  #print(json.dumps(data['links'],sort_keys=True,indent=4))
  linkname=getKeyByValue(data['links'],'^my_items\.php\?deleteid=(.*)')
  if linkname:
    relativeurl=data['links'][linkname]
    print(relativeurl)
    return relativeurl
  return None

def anzeigen_loeschen(session,anzeige):

  relativeurl = get_next_delete_url(session)
  while(relativeurl):  
    print('- delete anzeige ',relativeurl)
    response = session.get(config['baseurl']+'/'+relativeurl)
    response.raise_for_status() # -> make sure it is 200
    html = response.text
    parser = DDHtmlParser()
    parser.feed(html)
    data=parser.return_data()
    relativeurl = get_next_delete_url(session)

  # print('title: ',anzeige['title'])
  # print('link: ',data['links'][anzeige['title']])
  # response = session.get(config['baseurl']+'/'+data['links'][anzeige['title']])
  # response.raise_for_status() # -> make sure it is 200
  # html = response.text
  # parser = DDHtmlParser()
  # parser.feed(html)
  # data=parser.return_data()

def anzeige_einstellen(session,anzeige):
  print('- start page')
  response = session.get(config['baseurl']+'/member.php')
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()

  # 'Anzeige eintragen' anklicken
  print('- Anzeige eintragen')
  response = session.get(config['baseurl']+'/'+data['links']['Anzeige eintragen'])
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()
  #print(json.dumps(data,sort_keys=True,indent=4))

  # Kategorie wählen
  print('- Kategorie wählen')
  catid=''
  for option in data['select']['catid']:
    if re.match('^'+anzeige['category']+' \(',option):
      catid=data['select']['catid'][option]
  if catid=='': raise("Kategorie "+category+' not found.')
  url=config['baseurl']+'/item.php'
  params = {'catid': catid }
  response = session.post(url, data=params)
  response.raise_for_status() # -> make sure it is 200
  #html = response.text
  #parser = DDHtmlParser()
  #parser.feed(html)
  #data=parser.return_data()
  #print(json.dumps(data,sort_keys=True,indent=4))

  print('- Anzeige einstellen')
  url=config['baseurl']+'/item.php'
  params = {'sitecatid': catid,
            'sitetitle': anzeige['title'],
            'sitedescription': anzeige['text'],
            'e_1': anzeige['price'].encode('utf-8'),
            'e_2': anzeige['place'],
            'expire_days': '30',
            'siteid': '',
            'submit': 'Weiter zum Bildupload'}
  response = session.post(url, data=params)
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()
  #print(html)

  #print(json.dumps(data['links'],indent=4))
  print('- Weiter zum Bild hochladen')
  #print(json.dumps(data['links'],indent=4))
  #print('getKeyByValue: '+getKeyByValue(data['links'],'upload_file\.php\?pictures_siteid='))
  #print('getValue: '+data['links'][getKeyByValue(data['links'],'upload_file\.php\?pictures_siteid=')])
  response = session.get(config['baseurl']+'/'+data['links'][getKeyByValue(data['links'],'upload_file\.php\?pictures_siteid=')])
  response.raise_for_status() # -> make sure it is 200
  html = response.text
  parser = DDHtmlParser()
  parser.feed(html)
  data=parser.return_data()

  for picture in reversed(anzeige['pictures']):
    http_client.HTTPConnection.debuglevel = 0
    print('- Bild hochladen: ',picture)
    url=config['baseurl']+'/'+'upload_file.php'
    params = {'pictures_siteid': data['form']['upload_file.php']['input']['pictures_siteid'],
              'MAX_FILE_SIZE': data['form']['upload_file.php']['input']['MAX_FILE_SIZE'],
              'submit': 'Hochladen'}
    with open(picture,mode='rb') as f:
      # mimetypes.types_map['.tgz']
      response = session.post(url, data=params, files={'photo':[os.path.basename(picture),f,'image/jpeg']})
    response.raise_for_status() # -> make sure it is 200
    html = response.text
    parser = DDHtmlParser()
    parser.feed(html)
    data=parser.return_data()
    #print(html)

config=readConfig()

anzeige = Anzeige(config[anzeigenpath])
print(anzeige)

session=login()
anzeigen_loeschen(session,anzeige)
anzeige_einstellen(session,anzeige)

