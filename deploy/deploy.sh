#!/bin/bash

echo 'Run as sudo'

# exit this script if any command returns a non-zero exit code
set -e

GIT_SSH_COMMAND="ssh -i /home/ubuntu/.ssh/id_rsa" git pull
chown -hR ubuntu /home/ubuntu/tobacco_networks/.git

source /home/ubuntu/tobacco_networks/venv/bin/activate

echo 'Building frontend'
cd /home/ubuntu/tobacco_networks/frontend
npm install
npm run build

cd ../backend

python manage.py collectstatic --noinput

supervisorctl restart tobacco_networks
