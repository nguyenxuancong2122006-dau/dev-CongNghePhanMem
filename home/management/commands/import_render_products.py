import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Import categories and products from products_data.json"

    def handle(self, *args, **options):
        data_file = Path("products_data.json")

        if not data_file.exists():
            self.stderr.write(self.style.ERROR("Không tìm thấy products_data.json"))
            return

        with data_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        call_command("loaddata", str(data_file))
        self.stdout.write(self.style.SUCCESS(
            f"Đã nhập {len(data)} bản ghi danh mục và sản phẩm."
        ))