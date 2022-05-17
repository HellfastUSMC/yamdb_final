import csv
import os

from django.apps import apps
from django.core.management import BaseCommand
from django.core.management.base import CommandError
from django.db import models, transaction


class Load():
    """Класс загрузчик данных из csv"""

    def __init__(self, file, model_name, app='reviews',
                 folder='/static/data/'):
        """Конструктор"""
        self.folder = '.' + folder
        self.file = file
        self.model_name = model_name
        self.app = app
        self.model = self._get_model_by_name()
        self.file_data = None
        self.file_child_data = None

        self._fill_model()

    def _get_file_path(self, file):
        """Полный путь к файлу"""
        return self.folder + file

    def _get_model_by_name(self):
        """Получить модель по имени"""
        Model = apps.get_model(self.app, self.model_name)

        if not Model:
            raise Exception('Модель %s не найдена' % (Model))

        return Model

    def _get_data_from_file_csv(self, filename):
        """Получить данные из csv файла"""
        file = self._get_file_path(filename)
        if not os.path.exists(file):
            raise Exception('Файл %s не найден' % (file))

        with open(file, "r", encoding="utf-8") as csv_file:
            file_data = list(csv.reader(csv_file, delimiter=","))

        if not file_data:
            raise Exception('Файл пуст')

        return file_data

    def _check_field(self, field_model, field_data):
        """Проверка поля модели на тип"""
        type_field = self.model._meta.get_field(field_model)

        if isinstance(type_field, models.ForeignKey):
            foreign_model = (self.model._meta.get_field(
                field_model).related_model)
            pk = foreign_model.objects.get(id=field_data)
            return (field_model, pk)

        return (field_model, field_data)

    def _get_data_from_child_file(self, id, child_field):
        """Получение данных для подчиненного поля"""
        data_fields = self.file_child_data[0]

        for i, field_name in enumerate(data_fields):
            data_fields[i] = field_name.lower().replace(
                ' ', '_').replace('_id', '')

        id_root_field = data_fields.index(self.model_name.lower())
        if not id_root_field:
            raise Exception(
                'Не найден столбец %s_id в подчиненном файле'
                % (self.model_name))

        id_child_field = data_fields.index(child_field)
        if not id_child_field:
            raise Exception(
                'Не найден столбец %s_id в подчиненном файле'
                % (child_field))

        filtered = list(
            filter(lambda x: (x[id_root_field] == str(id)),
                   self.file_child_data[1:]))

        result = []

        for filtered_row in filtered:
            child_model = self.model._meta.get_field(
                child_field).related_model
            pk = child_model.objects.get(id=filtered_row[id_child_field])
            result.append(pk)

        return result

    def fill_model_foregin_key(self, file_child_data, child_field):
        """Заполнение подчиненного поля данными"""

        if None in (file_child_data, child_field, self.model):
            raise Exception(
                'Нехватает данных для заполнения child_field - %s!'
                ' file_child_data - %s self.model -%s'
                % (child_field, file_child_data, self.model))

        print(f'Заполняем {self.app}.{self.model_name}.{child_field} ...')
        self.file_child_data = self._get_data_from_file_csv(file_child_data)
        added_rows = self.model.objects.all()

        for row in added_rows:
            child_field_obj = getattr(row, child_field)
            child_data_list = self._get_data_from_child_file(
                row.id, child_field)
            child_field_obj.all().delete()
            if child_data_list:
                child_field_obj.add(*child_data_list)

        print(f'Данные {self.app}.{self.model_name}.{child_field}'
              ' заполнены')

    def _fill_model(self):
        """Зполнение модели основная функция"""
        file_data = self._get_data_from_file_csv(self.file)
        model_fields = [f.name for f in self.model._meta.fields]
        fields_name = file_data[0]

        for i, field_name in enumerate(fields_name):
            fields_name[i] = field_name.lower().replace(
                ' ', '_').replace('_id', '')

            if not fields_name[i] in model_fields:
                raise Exception('Поле %s не найдено в модели %s' %
                                (fields_name[i], self.model))

        insert_list = []
        print(f'Заполняем Модель {self.app}.{self.model_name} ...')
        for row in file_data[1:]:
            obj = self.model()

            for i, field in enumerate(row):
                fields_name[i], field = self._check_field(
                    fields_name[i], field)
                setattr(obj, fields_name[i], field)

            insert_list.append(obj)

        self.model.objects.all().delete()
        self.model.objects.bulk_create(insert_list)
        print(f'Модель {self.app}.{self.model_name} успешно заполнена')


class Command(BaseCommand):
    help = 'Команда для загрузки данных из csv в Модели'

    @transaction.atomic
    def handle(self, *args, **options):

        confirm = input('Вы запускаете импорт в базу данных из csv файлов.'
                        ' Все текущие данные будут удалены.'
                        ' Запустить импорт? (Y/n)')
        while 1:
            if confirm not in ('Y', 'n', 'yes', 'no'):
                confirm = input('Введите "yes" or "no": ')
                continue
            if confirm in ('Y', 'yes'):
                break
            else:
                return

        try:
            sid = transaction.savepoint()
            model_obj = Load('genre.csv', 'Genre')
            del model_obj
            model_obj = Load('category.csv', 'Category')
            del model_obj
            model_obj = Load('titles.csv', 'Title')
            model_obj.fill_model_foregin_key('genre_title.csv', 'genre')
            del model_obj
            model_obj = Load('users.csv', 'User', app='users')
            del model_obj
            model_obj = Load('review.csv', 'Review')
            del model_obj
            model_obj = Load('comments.csv', 'Comment')
            del model_obj

            transaction.savepoint_commit(sid)

        except Exception as e:
            transaction.savepoint_rollback(sid)
            self.stdout.write(self.style.ERROR('ERROR'))
            raise CommandError(e)
