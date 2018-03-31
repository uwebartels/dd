from html.parser import HTMLParser
import json

class DDHtmlParser(HTMLParser):
  mytags=[]
  
  def __init__(self):
    HTMLParser.__init__(self)
    self.mydata = {'links': {},'select': {},'forms': {}} 
    self.myignoretags = ['meta','link','img','font','br','p','b','input']
    self.myhref = ''
    self.myselect = ''
    self.myoptionvalue = ''
    self.myform={}

  def handle_starttag(self, tag, attrs):
    #if showparserdetails: print("Encountered a start tag:", tag, json.dumps(dict(attrs)))
    if tag not in self.myignoretags:
      #print("Encountered a start tag:", tag, json.dumps(self.mytags))
      self.mytags.append(tag)
    if tag == 'a':
      self.myhref = attrs[0][1]
    if tag == 'option':
      self.myoptionvalue = attrs[0][1]
    if tag == 'select':
      self.myselect=dict(attrs)['name']
      # collect <select>'s
      self.mydata['select'][self.myselect]={}
    if tag == 'form':
      attributes=dict(attrs)
      self.myform=attributes['action']
      self.mydata['forms'][attributes['action']]=attributes
      self.mydata['forms'][attributes['action']]['input']={}
    if tag == 'input':
      attributes=dict(attrs)
      if 'name' in attributes and 'value' in attributes:
        self.mydata['forms'][self.myform]['input'][attributes['name']]=attributes['value']


  def handle_endtag(self, tag):
    #print("Encountered an end tag :", tag)
    if tag == 'a':
      found=False
      for name, href in self.mydata['links'].items():
        if self.myhref == href:
          found=True
          break
      if not found:
        self.mydata['links'][self.myhref]=self.myhref

    if tag not in self.myignoretags:
      #print("Encountered an end tag:", tag, json.dumps(self.mytags))
      while (self.mytags.pop() != tag): 
        print("Encountered an unregistered end tag :", tag)
        pass

  def handle_data(self, data):
    #global showparserdetails
    if len(self.mytags) == 0: return
    encodeddata=data.encode('utf-8')
    #print('encodeddata: ',encodeddata)
    # collect all link names
    if self.mytags[len(self.mytags)-1] == 'a':
      self.mydata['links'][data]=self.myhref
    # collect all select options
    if len(self.mytags) > 0 and self.mytags[len(self.mytags)-1] == 'option':
      self.mydata['select'][self.myselect][data]=self.myoptionvalue
      #if showparserdetails: print("'"+"','".join(self.mytags)+"'")
      #if showparserdetails: print("Encountered data :", encodeddata)

  def return_data(self):
      return self.mydata
