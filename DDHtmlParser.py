from html.parser import HTMLParser
import json,re

import logging

log = logging.getLogger(__name__)

class DDHtmlParser(HTMLParser):
  
  def __init__(self):
    HTMLParser.__init__(self)
    self.mydata = {'links': {},'select': {},'forms': {},'meta':{'http-equiv':{},'name':{},'property':{}},'ddanzeige':{},'ddanzeigendetails':{}}
    self.myignoretags = ['link','img','font','br','p','b','input']
    self.myformattags = ['u','b','strike']
    self.mytags=[]
    self.myhref = ''
    self.myselect = ''
    self.myoptionvalue = ''
    self.myform={}

  def handle_starttag(self, tag, attrs):
    # collect starting tags in a list
    if tag not in self.myignoretags:
      if tag not in ['meta']:
        self.mytags.append(tag)

    # memorize link href for connecting with text to the link
    if tag == 'a':
      self.myhref = attrs[0][1]

    # memorize select option href for connecting with select tag
    if tag == 'option':
      self.myoptionvalue = attrs[0][1]

    # collect selects
    if tag == 'select':
      self.myselect=dict(attrs)['name']
      self.mydata['select'][self.myselect]={}

    # collect forms
    if tag == 'form':
      attributes=dict(attrs)
      self.myform=attributes['action']
      self.mydata['forms'][attributes['action']]=attributes
      self.mydata['forms'][attributes['action']]['input']={}

    # collect input tags
    if tag == 'input':
      attributes=dict(attrs)
      if 'name' in attributes and 'value' in attributes:
        self.mydata['forms'][self.myform]['input'][attributes['name']]=attributes['value']

    # collect meta tags
    if tag == 'meta':
      attributes=dict(attrs)
      if 'http-equiv' in attributes:
        # <meta http-equiv="content-type" content="text/html; charset=iso-8859-1">
        self.mydata['meta']['http-equiv'][attributes['http-equiv']]=attributes['content']
      elif 'name' in attributes:
        # <meta name="language" content="de">
        self.mydata['meta']['name'][attributes['name']]=attributes['content']
      elif 'property' in attributes:
        # <meta property="og:image" content="http://www.dailydose.de/private-kleinanzeigen/aaa04.jpg">
        self.mydata['meta']['property'][attributes['property']]=attributes['content']
      else:
        log.warn("Unhandled meta tag: "+json.dumps(attributes))

  def handle_endtag(self, tag):
    realtag = tag
    # put in a loop!!
    if tag in self.myformattags:
      # next to last element (vorletztes)
      realtag = self.mytags[-2:-1:]

    if realtag == 'a':
      found=False
      for name, href in self.mydata['links'].items():
        if self.myhref == href:
          found=True
          break
      if not found:
        self.mydata['links'][self.myhref]=self.myhref

    if tag not in self.myignoretags:
      while (self.mytags.pop() != tag): 
        log.warn("Encountered an unregistered end tag : "+tag)
        pass

  def handle_data(self, data):
    if len(self.mytags) == 0: return
    # collect all link names
    if self.mytags[len(self.mytags)-1] == 'a':
      self.mydata['links'][data]=self.myhref
    # collect all select options
    if len(self.mytags) > 0 and self.mytags[len(self.mytags)-1] == 'option':
      self.mydata['select'][self.myselect][data]=self.myoptionvalue

    # detail page für one advertisement
    ## initialize result data for next <td> element
    if self.mytags[len(self.mytags)-1] == 'td':
      if data=='Preis (EUR)':
        self.mydata['ddanzeigendetails']['price']=''
        return
      if data=='Ort':
        self.mydata['ddanzeigendetails']['place']=''
        return
      if data==' Verkäufer':
        self.mydata['ddanzeigendetails']['seller']=''
        return
      if data==' Telefon':
        self.mydata['ddanzeigendetails']['tel']=''
        return
      if data==' Datum':
        self.mydata['ddanzeigendetails']['date']=''
        return

      if 'price' in self.mydata['ddanzeigendetails']:
        if self.mydata['ddanzeigendetails']['price']=='':
          self.mydata['ddanzeigendetails']['price']=data.strip()
      if 'place' in self.mydata['ddanzeigendetails']:
        if self.mydata['ddanzeigendetails']['place']=='':
          self.mydata['ddanzeigendetails']['place']=data.strip()
      if 'seller' in self.mydata['ddanzeigendetails']:
        if self.mydata['ddanzeigendetails']['seller']=='':
          self.mydata['ddanzeigendetails']['seller']=data.strip()
      if 'tel' in self.mydata['ddanzeigendetails']:
        if self.mydata['ddanzeigendetails']['tel']=='':
          self.mydata['ddanzeigendetails']['tel']=data.strip()
      if 'date' in self.mydata['ddanzeigendetails']:
        if self.mydata['ddanzeigendetails']['date']=='':
          self.mydata['ddanzeigendetails']['date']=data.strip()

    # identifies one advertisement
    match = re.match('detail\.php\?siteid=(\d+)',self.myhref)
    if match:
      anzeigeID = match.group(1)
      if anzeigeID not in self.mydata['ddanzeige']:
        self.mydata['ddanzeige'][anzeigeID]=data


  def return_data(self):
      return self.mydata
