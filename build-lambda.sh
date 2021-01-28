#!/bin/sh

files="checkhotsails.py DDConfig.py DDHtmlParser.py DDSession.py"
for f in $files;do
  cp $f ../ddlambda/
done
cd ../ddlambda
rm -f ../ddlambda.zip
zip -r ../ddlambda.zip *

