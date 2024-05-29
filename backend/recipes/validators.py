from django.core.exceptions import ValidationError


def validate_time_amount(data):
    if data < 1:
        raise ValidationError(
            'Значение не может быть меньше 1'
        )
