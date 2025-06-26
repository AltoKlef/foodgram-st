import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из файла ingredients.csv'

    def handle(self, *args, **options):
        file_path = Path('./data/ingredients.csv')
        if not file_path.exists():
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не найден"))
            return

        with file_path.open(encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            count = 0
            for row in reader:
                if len(row) != 2:
                    self.stdout.write(self.style.WARNING(
                        f"Пропущена строка: {row}"
                    ))
                    continue
                name, unit = row
                Ingredient.objects.get_or_create(
                    name=name.strip(), measurement_unit=unit.strip()
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Импортировано {count} ингредиентов")
        )
