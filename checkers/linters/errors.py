# -*- encoding: utf-8 -*-

try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser


class CheckError():
    """Класс представления ошибки"""
    def __init__(self, *args, **kwargs):
        self.line_start = None
        self.line_end = None
        self.column_start = None
        self.column_end = None
        self.message = None
        self.severity = None
        self.type = None

        severities_available = ['error', 'warning']

        # Линия начала ошибки
        self.line_start = kwargs.get('line_start', None)

        # Линия конца ошибки
        self.line_end = kwargs.get('line_end', None)

        # Колонка начала ошибки
        self.column_start = kwargs.get('column_start', None)

        # Колонка конца ошибки
        self.column_end = kwargs.get('column_end', None)

        # Суровость ошибки
        self.severity = kwargs.get('severity', severities_available[0])

        if not self.severity:
            self.severity = severities_available[0]

        if self.severity not in severities_available:
            exeption = "Wrong error severity: {severity}. Available types are: {types}".format(
                severity=self.type,
                types=severities_available)
            raise Exception(exeption)

        # Сообщение ошибки
        self.message = kwargs.get('message', None)

        # Тип ошибки
        self.type = kwargs.get('type', None)

    def get_line(self):
        return self.line

    def get_message(self):
        data = self.message

        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            """"""
            # ошибка декодирования в лог

        return HTMLParser().unescape(data)
