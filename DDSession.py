
import json,requests,re,os
from DDHtmlParser import DDHtmlParser

import logging
import mimetypes

log = logging.getLogger(__name__)

class DDSession:

  def __init__(self,config):
    self.config = self.__readConfig(config)
    self.session=None

    self.lastresponse=None
    self.lasthtml=None
    self.lastdata=None

    self.__login()

  def __getitem__(self, key):
    if key == 'config': return self.config
    #elif key == 'price': return self.price

  def __readConfig(self,configfile):
    return json.load(open(configfile))["dd"]

  def __processResponse(self):
    self.lastresponse.raise_for_status() # -> make sure it is 200
    self.lasthtml = self.lastresponse.text
    parser = DDHtmlParser()
    parser.feed(self.lasthtml)
    self.lastdata=parser.return_data()

  def __login(self):
    self.session = requests.Session() 

    # login
    log.info("- Login")
    url=self.config['baseurl']+'/member_login.php'
    log.debug("url: "+url)
    params = {'redirect_to': '', 'username': self.config['username'], 'password': self.config['password'], 'submit':'Einloggen'}
    log.debug("params: "+json.dumps(params))
    self.lastresponse = self.session.post(url, data=params)
    self.lastresponse.raise_for_status() # -> make sure it is 200

    # page after login
    log.info("- Seite Mitgliederbereich")
    url=self.config['baseurl']+'/member.php'
    log.debug("url: "+url)
    self.lastresponse = self.session.get(url)
    self.__processResponse()

  def __getKeyByValue(self,dict,regexp):
    for key,value in dict.items():
      match=re.match(regexp,value)
      if match:
        return key

  def __getNextDeleteUrl(self):

    self.lastresponse = self.session.get(self.config['baseurl']+'/member.php')
    self.__processResponse()

    try:
      self.lastresponse = self.session.get(self.config['baseurl']+'/'+self.lastdata['links']['Anzeige(n) bearbeiten'])
    except Exception:
      log.debug(json.dumps(data['links'],indent=4))
      raise
    self.__processResponse()

    linkname=self.__getKeyByValue(self.lastdata['links'],'^my_items\.php\?deleteid=(.*)')
    if linkname:
      relativeurl=self.lastdata['links'][linkname]
      return relativeurl
    return None

  def anzeigenLoeschen(self):
    relativeurl = self.__getNextDeleteUrl()
    while(relativeurl):  
      log.info('- delete anzeige '+relativeurl)
      self.lastresponse = self.session.get(self.config['baseurl']+'/'+relativeurl)
      self.__processResponse()
      relativeurl = self.__getNextDeleteUrl()

  def anzeigeEinstellen(self,anzeige):
    log.info('- start page')
    self.lastresponse = self.session.get(self.config['baseurl']+'/member.php')
    self.__processResponse()

    # 'Anzeige eintragen' anklicken
    log.info('- Anzeige eintragen: '+anzeige['title'])
    self.lastresponse = self.session.get(self.config['baseurl']+'/'+self.lastdata['links']['Anzeige eintragen'])
    self.__processResponse()

    # Kategorie wählen
    log.info('- Kategorie wählen: '+anzeige['category'])
    catid=''
    for option in self.lastdata['select']['catid']:
      if re.match(anzeige['category']+' \(',option):
        catid=self.lastdata['select']['catid'][option]
    if catid=='': raise("Kategorie "+category+' not found.')
    url=self.config['baseurl']+'/item.php'
    params = {'catid': catid }
    self.lastresponse = self.session.post(url, data=params)
    self.__processResponse()

    log.info('- Anzeige einstellen')
    url=self.config['baseurl']+'/item.php'
    params = {'sitecatid': catid,
              'sitetitle': anzeige['title'],
              'sitedescription': anzeige['text'],
              'e_1': anzeige['price'].encode('utf-8'),
              'e_2': anzeige['place'],
              'expire_days': '30',
              'siteid': '',
              'submit': 'Weiter zum Bildupload'}
    self.lastresponse = self.session.post(url, data=params)
    self.__processResponse()

    log.info('- Weiter zum Bild hochladen')
    self.lastresponse = self.session.get(self.config['baseurl']+'/'+self.lastdata['links'][self.__getKeyByValue(self.lastdata['links'],'upload_file\.php\?pictures_siteid=')])
    self.__processResponse()

    for picture in reversed(anzeige['pictures']):
      self.__uploadPicture(picture)

    if anzeige['isReserved']:
      self.__setReserved()

  def __uploadPicture(self,picture):
    log.info("- Uploading Picture "+os.path.basename(picture))
    url=self.config['baseurl']+'/'+'upload_file.php'
    params = {'pictures_siteid': self.lastdata['form']['upload_file.php']['input']['pictures_siteid'],
              'MAX_FILE_SIZE': self.lastdata['form']['upload_file.php']['input']['MAX_FILE_SIZE'],
              'submit': 'Hochladen'}
    with open(picture,mode='rb') as f:
      root,extension=os.path.splitext(picture)
      mimetype=mimetypes.types_map[extension.lower()]
      self.lastresponse = self.session.post(url, data=params, files={'photo':[os.path.basename(picture),f,mimetype]})
      self.__processResponse()

  def __setReserved(self):
      log.info('- Anzeige(n) bearbeiten')
      self.lastresponse = self.session.get(self.config['baseurl']+'/'+self.lastdata['links']['Anzeige(n) bearbeiten'])
      self.__processResponse()

      link=self.lastdata['links'][anzeige['title']]
      match=re.match('^detail\.php\?siteid=(\d+)$',link)
      if match:
        anzeigeid=match.group(1)
        log.info('- Anzeige Reserviert')
        self.lastresponse = self.session.get(self.config['baseurl']+'/my_items.php?soldid='+anzeigeid)
        self.__processResponse()

