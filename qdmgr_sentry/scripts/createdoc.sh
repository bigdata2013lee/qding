#!  /bin/bash

export PYTHONPATH=$PYTHONPATH:/data/qding/qdmgr_sentry
cd  /data/qding/qdmgr_sentry

files='\
./apps/common/api/brake_api.py  \
./apps/common/api/user_api.py    \
./apps/common/api/sentry_api.py    \
./apps/common/api/basedata_api.py \
'


epydoc --output='/data/qding/qdmgr_sentry/api_doc' --name='Qding Sentry Api' $files
