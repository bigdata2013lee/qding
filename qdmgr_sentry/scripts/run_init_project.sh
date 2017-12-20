#! /bin/bash

ROOT_DIR="/data/qding"
SOFT_DIR="$ROOT_DIR/software"
PYTHON=$ROOT_DIR/python/bin/python3
PIP=$ROOT_DIR/python/bin/pip3




function installPy(){
    if [ ! -d $SOFT_DIR/$1 ];then
        echo "$SOFT_DIR/$1 not exists"
        return
    fi
    cd $SOFT_DIR/$1
    $PYTHON setup.py install
}


function makeInstall(){
    if [ ! -f $SOFT_DIR/$1 ];then
        echo "$SOFT_DIR/$1 not exists"
        return
    fi
    cd $SOFT_DIR
    tar xf $SOFT_DIR/$1
    cd $SOFT_DIR/$2
    ./configure --prefix=$3
    make
    make install
}

function checkEnv(){
    if [ -d $ROOT_DIR/python.bak ];then
        echo "$ROOT_DIR/python.bak exists"
        return 1
    fi
    if [ -d $ROOT_DIR/python ];then
        mv $ROOT_DIR/python $ROOT_DIR/python.bak
    fi
    if [ ! -d $SOFT_DIR ];then
        echo "$SOFT_DIR not exists"
        return 2
    fi
    makeInstall "Python-3.4.4.tgz" "Python-3.4.4" "$ROOT_DIR/python"
}

function initProject(){
    checkEnv
    if [ $? -ne 0 ];then
        return
    fi

    installPy "Django-1.7.4"
    installPy "django-hosts-1.2"
    installPy "django-jinja-1.4.1"
    installPy "django-extensions-1.5.5"
    installPy "mongoengine"
    installPy "aiohttp"
    installPy "PyMySQL-0.7.5"
    installPy "redis-2.10.5"

    installPy "Werkzeug-0.11.10"
    installPy "requests-2.10.0"
    installPy "Pillow-2.3.0"
    installPy "uwsgi-2.0.13.1"
    echo "=======================================pip list ========================="
    $PIP list
}



mkdir -p $ROOT_DIR
mkdir -p $SOFT_DIR
tar xf software.tar.gz -C $ROOT_DIR
initProject
ln -sf /data/qding/python/bin/python3 /usr/bin/
ln -sf /data/qding/python/bin/pip3 /usr/bin
ln -sf /data/qding/python/bin/uwsgi /usr/bin/