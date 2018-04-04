import os,io,json,stat
import logging
log = logging.getLogger(__name__)

class DDConfig:
  filename='dd.json'
  baseurl='https://www.dailydose.de/private-kleinanzeigen'

  def __init__(self):
    self.config={}
    if os.path.isfile(self.filename):
      # simply read the config file
      self.config = json.load(open(self.filename))
    else:
      # generate a config file interactively
      self.config=self.__generateConfig()

    self.config['baseurl']=self.baseurl

  def __generateConfig(self):
    username = input('dailydose Login: ')
    password = input('dailydose Passwort: ')
    path = input('Verzeichnis mit Anzeigen: ')
    self.config['username']=username
    self.config['password']=password
    self.config['anzeigenpath']=path
    umask = 0o066 # create file with 0600 -rw------- only owner can read+write
    umask_original = os.umask(umask)
    with io.open(self.filename, 'w', encoding='utf-8') as f:
      f.write(json.dumps(self.config,indent=4, ensure_ascii=False))
    os.umask(umask_original)
    log.info("Konfiguration in "+self.filename+" gespeichert.")
    return self.config

  def __getitem__(self, key):
    return self.config[key]


