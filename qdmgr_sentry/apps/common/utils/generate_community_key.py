from django.conf import settings
import subprocess


def generate_qdkey(groupId):
    cmd = 'chmod +x %s/static/sentry/thirdparty/generate-qdkey; %s/static/sentry/thirdparty/generate-qdkey %s'
    cmd = cmd % (settings.BASE_DIR, settings.BASE_DIR, str(groupId))
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout_data, stderr_data) = process.communicate()
    enc_key = stdout_data.decode('utf8').strip().split('\n')[0][-10:]
    dec_key = stdout_data.decode('utf8').strip().split('\n')[1][-10:]

    return (enc_key, dec_key)
