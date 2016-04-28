#!/bin/bash

# os dependencies
sudo sh ./install_os_dependencies.sh install

# python dependencies
# pip
pip --version >/dev/null 2>&1 || {
    echo "\nInstalling pip."
    wget https://bootstrap.pypa.io/get-pip.py --output-document=get-pip.py; chmod +x get-pip.py; sudo -H python2 get-pip.py
}

virtualenv --version >/dev/null 2>&1 || {
    echo "\nInstalling virtualenv."
    sudo pip2 install virtualenv
}

VIRTUAL_PATH=~/.virtualenvs/delete
if [ -z "$VIRTUAL_ENV" ]; then
    mkdir -p ${VIRTUAL_PATH}
    virtualenv ${VIRTUAL_PATH} --python=`which python2`
    echo "\nPlease run the following command to activate the new virtualenv:"
    echo "source ${VIRTUAL_PATH}/bin/activate"
    exit 1;
else
    pip install -r ../requirements/production.txt
    cd ..
    python manage.py migrate
#    echo starting the server...
#    python manage.py runserver 0.0.0.0:80
#    gunicorn orchid.wsgi:application --bind 0.0.0.0:80
##    start the celery daemon
#    echo starting celery...
#    python manage.py celery worker --loglevel=info
fi
