# --*-- coding: utf8 --*--
from django.core.management.base import BaseCommand

from apps.common.utils.xutil import start_process
from apps.async.pass_data_collector import collect
from apps.async.base_data_synchronizer import sync_base_data
from apps.async.excel_data_exporter import dump_data
from apps.async.open_door_list_updater import update_app_user
from apps.async.low_frequency_processor import update_process
from apps.async.password_sender import send_password_to_cloud_talker


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) == 0:
            start_process(collect)
            start_process(collect)
            start_process(collect)
            start_process(collect)
            start_process(sync_base_data)
            start_process(dump_data)
            start_process(update_app_user)
            start_process(update_process)
            start_process(send_password_to_cloud_talker)
            return
        if args[0] == 'collect':
            start_process(collect)
        elif args[0] == 'base_data':
            start_process(sync_base_data)
        elif args[0] == 'excel_data':
            start_process(dump_data)
        elif args[0] == 'door_update':
            start_process(update_app_user)
        elif args[0] == 'update_process':
            start_process(update_process)
        elif args[0] == 'send_password_to_cloud_talker':
            start_process(send_password_to_cloud_talker)
