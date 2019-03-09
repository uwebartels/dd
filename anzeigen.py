#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# tested with python 3.3.2
import sys
if sys.version_info < (3, 3):
    raise "must use python 3.3 or greater"

import os,logging,traceback
from DDSession import DDSession
from Anzeige import Anzeige

# logging initializing
import http.client as http_client
http_client.HTTPConnection.debuglevel = 0
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = False
log = logging.getLogger(__name__)

ignoreFileList=['.DS_Store']

# login to daildose
session=DDSession()
session.login()
# delete all ads
session.anzeigenLoeschen()

# add all adds
exceptions=[]
dirs = sorted(os.listdir(session.config['anzeigenpath']))
for dir in dirs:
  absolutepathdir=os.path.join(session.config['anzeigenpath'],dir)

  # only directories here please
  if not os.path.isdir(absolutepathdir):
    if dir not in ignoreFileList:
      log.warn("Datei "+absolutepathdir+" wird ignoriert.")
    continue

  try:
    # load advertisement
    anzeige = Anzeige(absolutepathdir)
    # upload advertisement in daildose
    session.anzeigeEinstellen(anzeige)
  except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    log.error('Fehler beim Einstellen der Anzeige '+anzeige['title'])
    exeption_hash = {'title':anzeige['title'],
                     'exception':e,
                     'exc_type':exc_type,
                     'exc_value':exc_value,
                     'exc_traceback':exc_traceback}
    # collect all errors and go on
    exceptions.append(exeption_hash)

# print all errors in detail
if len(exceptions)>0:
  for e in exceptions:
    print()
    print('Error in '+e['title'])
    print('=================================')
    traceback.print_exception(e['exc_type'], e['exc_value'], e['exc_traceback'],limit=5, file=sys.stderr)
  sys.exit(1)

sys.exit(0)