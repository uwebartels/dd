import os,re

class Anzeige:
  truestrings=['ja','true','yes','Ja','JA','Yes','YES']

  def __init__(self,directory):
    self.directory=directory
    self.title=''
    self.text=''
    self.price=''
    self.category=''
    self.place=''
    self.isReserved=False
    self.pictures=[]

    files = sorted(os.listdir(directory))
    pictures=0
    for filename in sorted(files):
      if re.match('^\.',filename): continue
      if filename == 'text.txt':
        self.__readText()
      else:
        pictures+=1
        if pictures<=3:
          self.__readPicture(filename)
        else:
          print('WARNING - ignoring picture '+filename)

  def __to_boolean(self,string):
    if string in self.truestrings:
      return True
    else:
      return False

  def __readText(self):
    lines=0
    with open(os.path.join(self.directory,'text.txt')) as f:
      for line in f:
        lines += 1
        if lines <= 5:
          match = re.search('^(Titel|Preis|Kategorie|Ort|Reserviert): (.*)',line)
          if match:
            if   match.group(1) == 'Titel':       self.title      = match.group(2)
            elif match.group(1) ==  'Preis':      self.price      = match.group(2)
            elif match.group(1) ==  'Kategorie':  self.category   = match.group(2)
            elif match.group(1) ==  'Ort':        self.place      = match.group(2)
            elif match.group(1) ==  'Reserviert': self.isReserved = self.__to_boolean(match.group(2))
            else: raise Exception('Unbekanntes Element '+match.group(1)+' in '+os.path.join(directory,'text.txt')+'.')
          else:
            raise Exception('Die ersten 5 Zeilen sind für Titel, Preis, Kategorie, Ort und Reserviert.')
        else:
          self.text += line

  def __readPicture(self,filename):
    filebase,extension = os.path.splitext(filename)
    extension = extension[1:] # remove initial dot
    if extension not in ['jpg','jpeg','JPG','JPEG','gif','GIF','png','PNG']:
      raise Exception(filename+' with'+extension+' does not apear to be an picture. please check.')
    if len(self.pictures)<3:
      self.pictures.append(os.path.join(self.directory,filename))
    else:
      raise Exception("only 3 pictures are allowed.")

  def __repr__(self):
    return '\n'.join((('title: '+self.title,
                       'price: '+str(self.price),
                       'category: '+self.category,
                       'place: '+self.place,
                       'isReserved: '+self.isReserved,
                       'text: '+self.text,
                       'pictures: '+', '.join(self.pictures))))

  def __getitem__(self, key):
    if key == 'title': return self.title
    elif key == 'price': return self.price
    elif key == 'category': return self.category
    elif key == 'place': return self.place
    elif key == 'isReserved': return self.isReserved
    elif key == 'text': return self.text
    elif key == 'pictures': return self.pictures
