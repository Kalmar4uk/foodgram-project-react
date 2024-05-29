import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from recipes.constants import PATH_TO_FILE

MODELS = {
    'Ingredient': Ingredient
}


class Command(BaseCommand):
    help = 'Команда импорта .csv файлов'

    def add_arguments(self, parser):
        parser.add_argument('name_file', type=str, help='Название файла csv')
        parser.add_argument(
            '--name_model',
            type=str,
            help='Название модели для добавления из файла csv'
        )

    def handle(self, *args, **kwargs):
        name_file = kwargs['name_file']
        name_model = kwargs['name_model']
        name_model = name_model.title()
        model = MODELS[name_model]
        with open(
            f'{PATH_TO_FILE}{name_file}', 'r', encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile)
            for data in reader:
                model.objects.create(name=data[0], measurement_unit=data[1])
            self.stdout.write(
                self.style.SUCCESS('Данные из файла загружены')
            )
