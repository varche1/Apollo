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
        line_start = kwargs.get('line_start', None)
        self.line_start = int(line_start) if line_start else None

        # Линия конца ошибки
        line_end = kwargs.get('line_end', None)
        self.line_end = int(line_end) if line_end else None

        # Колонка начала ошибки
        column_start = kwargs.get('column_start', None)
        self.column_start = int(column_start) if column_start else None

        # Колонка конца ошибки
        column_end = kwargs.get('column_end', None)
        self.column_end = int(column_end) if column_end else None

        # Суровость ошибки
        severity = kwargs.get('severity', severities_available[0])
        self.severity = str(severity) if severity else None

        if not self.severity:
            self.severity = severities_available[0]

        if self.severity not in severities_available:
            exeption = "Wrong error severity: {severity}. Available types are: {types}".format(
                severity=self.type,
                types=severities_available)
            raise Exception(exeption)

        # Сообщение ошибки
        message = kwargs.get('message', None)
        self.message = str(message) if message else None

        # Тип ошибки
        type_error = kwargs.get('type', None)
        self.type = str(type_error) if type_error else None

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

    def get_error(self):
        return {
            "line_start":   self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end":   self.column_end,
            "message": self.message,
            "severity": self.severity,
            "type":   self.type
        }

    @staticmethod
    def serialize(obj):
        return {
            "line_start":   obj.line_start,
            "line_end": obj.line_end,
            "column_start": obj.column_start,
            "column_end":   obj.column_end,
            "message": obj.message,
            "severity": obj.severity,
            "type":   obj.type
        }
