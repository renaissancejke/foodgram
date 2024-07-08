from django.core.validators import RegexValidator

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='''Юзернейм должен состоять из букв, цифр
                или содержать следующие символы: .@+-''',
)
