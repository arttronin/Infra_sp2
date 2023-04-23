from django.core.exceptions import ValidationError
import re


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть <me>.',
            params={'value': value},
        )
    # Если все правильно понял, то должно быть так
# value = '$me!*)(A_'
# if re.search('^[a-zA-Z0-9_]+$', value) is None:
    # raise ValidatorError(
    #   (re.sub('[a-zA-Z0-9_]', '', value))
    if re.search(r'^[-a-zA-Z0-9_]+$', value) is None:
        raise ValidationError(
            ('Hе допустимые символы '), params={'value': value},)
