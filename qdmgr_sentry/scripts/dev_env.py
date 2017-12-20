# --*-- coding:utf8 --*--
import subprocess, random, os, datetime, sys, re

version = sys.version.split()[0]
version_re = re.compile('^2.*')

def my_print(out):
    if version_re.match(version):
        exec('print "%s"' % out)
    else:
        exec('print("%s")' % out)

def run_shell(shell_command):
    out, err = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return out.decode('utf8'), err


def get_soft_dir(source_code_path, tmp_dir_path):
    run_shell('tar xf %s -C %s' % (source_code_path, tmp_dir_path))
    out, err = run_shell('ls %s' % tmp_dir_path)
    soft_dir = tmp_dir_path + os.sep + out[:-1]
    return soft_dir


def source_install(source_code_path, tmp_dir_path, des_dir_name):
    soft_dir = get_soft_dir(source_code_path, tmp_dir_path)
    des_dir = install_dir + os.sep + des_dir_name
    run_shell('cd %s;./configure  --prefix=%s;make;make install' % (soft_dir, des_dir))
    run_shell('rm -rf %s' % soft_dir)
    run_shell('ln -sf %s/%s/bin/%s /usr/bin/' % (install_dir, des_dir_name, des_dir_name))
    run_shell('ln -sf %s/%s/bin/%s /usr/local/bin/' % (install_dir, des_dir_name, des_dir_name))


def python_install(source_code_path, tmp_dir_path):
    soft_dir = get_soft_dir(source_code_path, tmp_dir_path)
    run_shell('cd %s;python3 setup.py install' % soft_dir)
    run_shell('rm -rf %s' % soft_dir)


def get_tmp_path():
    tmp_dir_name = ''.join(random.choice('abcdefghijklmn') for x in range(5))
    return os.getcwd() + os.sep + tmp_dir_name


def mk_tmp_dir():
    tmp_dir_path = get_tmp_path()
    out, err = run_shell('ls %s' % tmp_dir_path)
    while out:
        tmp_dir_path = get_tmp_path()
        out, err = run_shell('ls %s' % tmp_dir_path)
    else:
        run_shell('mkdir %s' % tmp_dir_path)
    return tmp_dir_path


def mk_install_path():
    out, err = run_shell('ls %s' % install_dir)
    if not err:
        run_shell('mv %s %s%s.bak' % (install_dir, install_dir, datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
        run_shell('mkdir -p %s' % install_dir)
    else:
        run_shell('mkdir -p %s' % install_dir)


source_code_path = os.getcwd()
install_dir = '/data/qding/software'
python_pag_list = ['Django==1.7.4', 'pymysql==0.7.10', 'mongoengine==0.11.0', 'django_extensions==1.7.8',
                   'django_jinja==2.2.2', 'Werkzeug==0.12.1', 'django_hosts==2.0', 'aiohttp==2.0.6',
                   'async-timeout==1.2.0', 'redis==2.10.5', 'requests==2.13.0', 'xlwt==1.2.0']

try:
    # mk_install_path()
    # tmp_dir_path = mk_tmp_dir()
    # source_install(source_code_path + os.sep + 'Python-3.6.1.tgz', tmp_dir_path, 'python3')
    pip_command = install_dir + os.sep + 'python/bin/pip3'
    for python_pag in python_pag_list:
        run_shell('sudo %s install %s' % (pip_command, python_pag))
    out, err = run_shell('%s list' % pip_command)
    for pag in out[:-1].split('\n'):
        my_print(pag)
finally:
    pass
    # run_shell('rm -rf %s' % tmp_dir_path)
