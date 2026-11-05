import json
from pathlib import Path

from django.core.management import BaseCommand, call_command
from django.db import transaction


class Command(BaseCommand):
    help = "Import categories and products from products_data.json"

    def handle(self, *args, **options):
        data_file = Path("products_data.json")

        if not data_file.exists():
            self.stderr.write(self.style.ERROR("Không tìm thấy products_data.json"))
            return

        with data_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        with transaction.atomic():
            call_command("loaddata", str(data_file))

        self.stdout.write(
            self.style.SUCCESS(f"Đã import {len(data)} bản ghi.")
        )
