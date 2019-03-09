
import json,requests,re,os,sys
#sys.path.append(os.path.dirname(__file__))
from DDHtmlParser import DDHtmlParser
from DDConfig import DDConfig
from html.parser import HTMLParser

import logging
import mimetypes
import urllib

log = logging.getLogger(__name__)

class DDSession:
  ddDefaultEncoding='iso-8859-1'

  def __init__(self):
    self.config = DDConfig()

    self.lastresponse=None
    self.lasthtml=None
    self.lastdata=None
    self.lastencoding=None
    self.session = requests.Session() 

  def __getitem__(self, key):
    if key == 'config': return self.config

  def __get(self,relativeurl):
    url=self.config['baseurl']+'/'+relativeurl
    self.lastresponse = self.session.get(url)
    self.__processResponse()

  def __post(self,relativeurl,params, files=None):
    url=self.config['baseurl']+'/'+relativeurl
    log.debug("url: "+url)
    log.debug("params: "+json.dumps(params))
    parameter={}
    for key,value in params.items():
      parameter[key]=value.encode(self.lastencoding or self.ddDefaultEncoding)
    self.lastresponse = self.session.post(url, data=parameter, files=files)
    self.__processResponse()

  def __processResponse(self):
    self.lastresponse.raise_for_status() # -> make sure it is 200
    self.lasthtml = HTMLParser.unescape(HTMLParser, self.lastresponse.text)
    parser = DDHtmlParser()
    parser.feed(self.lasthtml)
    self.lastdata=parser.return_data()
    try:
      contenttype=self.lastdata['meta']['http-equiv']['content-type']
      # "text/html; charset=iso-8859-1"
      self.lastencoding=rematch('^.*charset=([^;]*).*',contenttype).group(1)
      log.info('content-type: '+contenttype)
      log.info('encoding: '+self.lastencoding)
    except Exception:
      pass

  def login(self):
    # login
    log.info("- Login")
    params = {'redirect_to': '', 'username': self.config['username'], 'password': self.config['password'], 'submit':'Einloggen'}
    self.__post('member_login.php',params)

    # page after login
    log.info("- Seite Mitgliederbereich")
    self.__get('member.php')

  def __getKeyByValue(self,dict,regexp):
    for key,value in dict.items():
      match=re.match(regexp,value)
      if match:
        return key

  def __getAnzeigeID(self,links,regexp):
    for key,value in links.items():
      match=re.match(regexp,value)
      if match:
        return match.group(1)

  def __getNextDeleteID(self):
    self.__get('member.php')
    self.__get(self.lastdata['links']['Anzeige(n) bearbeiten'])
    anzeigeID=self.__getAnzeigeID(self.lastdata['links'],'^my_items\.php\?deleteid=(.*)')
    if anzeigeID:
      return anzeigeID
    return None

  def __uploadPicture(self,picture):
    log.info("- Uploading Picture "+os.path.basename(picture))
    params = {'pictures_siteid': self.lastdata['forms']['upload_file.php']['input']['pictures_siteid'],
              'MAX_FILE_SIZE': self.lastdata['forms']['upload_file.php']['input']['MAX_FILE_SIZE'],
              'submit': 'Hochladen'}
    with open(picture,mode='rb') as f:
      root,extension=os.path.splitext(picture)
      mimetype=mimetypes.types_map[extension.lower()]
      self.__post('upload_file.php',params, files={'photo':[os.path.basename(picture),f,mimetype]})

  def __setReserved(self,anzeige):
    log.info('- Anzeige Reserviert')
    self.__get(self.lastdata['links']['Anzeige(n) bearbeiten'])
    link=self.lastdata['links'][anzeige['title']]
    match=re.match('^detail\.php\?siteid=(\d+)$',link)
    if match:
      anzeigeid=match.group(1)
      self.__get('my_items.php?soldid='+anzeigeid)
    else:
      raise Exception("Link '"+anzeige['title']+"' nicht gefunden.")

  def anzeigenLoeschen(self):
    anzeigeID=self.__getNextDeleteID()
    while(anzeigeID):
      link = 'my_items.php?deleteid='+anzeigeID
      log.info('- delete anzeige "'+self.lastdata['ddanzeige'][anzeigeID]+'"')
      self.__get(link)
      anzeigeID = self.__getNextDeleteID()
  
  def anzeigeEinstellen(self,anzeige):
    log.info('- start page')
    self.__get('member.php')

    # 'Anzeige eintragen' anklicken
    log.info('- Anzeige eintragen: '+anzeige['title'])
    self.__get(self.lastdata['links']['Anzeige eintragen'])

    # Kategorie wählen
    log.info('- Kategorie wählen: '+anzeige['category'])
    catid=''
    for option in self.lastdata['select']['catid']:
      if re.match(anzeige['category']+' \(',option):
        catid=self.lastdata['select']['catid'][option]
      if catid=='' and re.match(anzeige['category'],option):
        catid=self.lastdata['select']['catid'][option]
    if catid=='': raise Exception("Kategorie "+anzeige['category']+" nicht gefunden. Mögliche Kategorien: \n"+"\n".join(self.lastdata['select']['catid'].keys()))
    params = {'catid': catid }
    self.__post('item.php',params)

    log.info('- Anzeige einstellen')
    params = {'sitecatid': catid,
              'sitetitle': anzeige['title'],
              'sitedescription': anzeige['text'],
              'e_1': anzeige['price'],
              'e_2': anzeige['place'],
              'expire_days': '30',
              'siteid': '',
              'submit': 'Weiter zum Bildupload'}
    self.__post('item.php',params)

    log.info('- Weiter zum Bild hochladen')
    self.__get(self.lastdata['links'][self.__getKeyByValue(self.lastdata['links'],'upload_file\.php\?pictures_siteid=')])

    for picture in reversed(anzeige['pictures']):
      self.__uploadPicture(picture)

    if anzeige['isReserved']:
      self.__setReserved(anzeige)

  def dict2flatlist(self,hash):
    log.debug('dict2flatlist('+json.dumps(hash)+')')
    list=[]
    for key in hash:
      list.append(key)
      list.append(hash[key])
    log.debug('return dict2flatlist('+json.dumps(list)+')')
    return list

  def search(self,searches={'Masten':'ezzy','Segel':'hot sails'}):
    # get index.php for retrieving category ids
    self.__get('index.php')
    options = self.lastdata['select']['catid_search']
    #print(json.dumps(options,indent=4))
    anzeigen={}
    for key,search in searches.items():
      match=re.match('([^:]*):(.*)',search)
      if match:
        category=match.group(1)
        searchterm=match.group(2)
        log.info('search: '+category+', '+searchterm)
        catid=''
        for name,id in options.items():
          if re.match(category+' .*\(',name):
            catid=id
        if catid=='': raise Exception("Kategorie "+category+" nicht gefunden. Mögliche Kategorien: \n"+"\n".join(self.lastdata['select']['catid'].keys()))
        params={'searchword': searchterm,'catid_search': catid,'do_search':'Suchen'}
        url='search.php?do_search=Search'+'&'+urllib.parse.urlencode(params)
        self.__get(url)
        #print(json.dumps(self.lastdata['ddanzeige'],indent=4))
        lastanzeigen=self.lastdata['ddanzeige']
        for anzeigeid in lastanzeigen:
          anzeigen[anzeigeid]={}
          anzeigen[anzeigeid]['title']=lastanzeigen[anzeigeid]
          anzeigen[anzeigeid]['link']=self.config['baseurl']+'/'+'detail.php?siteid='+anzeigeid

          # retrieve ad details
          url='detail.php?siteid='+anzeigeid
          self.__get(url)
          anzeigen[anzeigeid].update(self.lastdata['ddanzeigendetails'])
          #log.debug('search: #anzeigen='+str(len(anzeigen)))
          #log.debug(json.dumps(anzeigen[anzeigeid],indent=4))
    #print(json.dumps(anzeigen,indent=4))
    #log.debug('end search: #anzeigen='+str(len(anzeigen)))
    return anzeigen







