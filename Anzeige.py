import os,re

class Anzeige:
  def __init__(self,directory):
    self.text=''
    self.pictures=[]
    files = sorted(os.listdir(directory))
    for filename in files:
      if re.match('^\.',filename): continue
      if filename == 'text.txt':
        lines=0
        with open(os.path.join(directory,'text.txt')) as f:
          for line in f:
            lines += 1
            if lines <= 4:
              match = re.search('^(Titel|Preis|Kategorie|Ort): (.*)',line)
              if match:
                if   match.group(1) == 'Titel':      self.title    = match.group(2)
                elif match.group(1) ==  'Preis':     self.price    = match.group(2)
                elif match.group(1) ==  'Kategorie': self.category = match.group(2)
                elif match.group(1) ==  'Ort':       self.place    = match.group(2)
                else: raise Exception('Unbekanntes Element '+match.group(1)+' in '+os.path.join(directory,'text.txt')+'.')
              else:
                raise Exception('Die ersten 4 Zeile sind für Titel, Preis, Kategorie und Ort.')
            else:
              self.text += line
      else:
        filebase,extension = os.path.splitext(filename)
        extension = extension[1:] # remove initial dot
        if extension not in ['jpg','jpeg','JPG','JPEG','gif','GIF','png','PNG']:
          raise Exception(filename+' with'+extension+' does not apear to be an picture. please check.')
        if len(self.pictures)<3:
          self.pictures.append(os.path.join(directory,filename))
        else:
          raise Exception("only 3 pictures are allowed.")

  def __repr__(self):
    return '\n'.join((('title: '+self.title,
                       'price: '+str(self.price),
                       'category: '+self.category,
                       'place: '+self.place,
                       'text: '+self.text,
                       'pictures: '+', '.join(self.pictures))))

  def __getitem__(self, key):
    if key == 'title': return self.title
    elif key == 'price': return self.price
    elif key == 'category': return self.category
    elif key == 'place': return self.place
    elif key == 'text': return self.text
    elif key == 'pictures': return self.pictures
