# -*- coding: utf-8 -*-

import os
import sys
from django.core.management import execute_from_command_line


DEV_CONFIG = "web.settings"

if __name__ == "__main__":
    version = sys.version_info
    if version.major != 3:
        print('\nPython version should be above 3.x\n')
        sys.stdout.flush()
        sys.exit(0)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEV_CONFIG)
    execute_from_command_line(sys.argv)


