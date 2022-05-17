from rest_framework.serializers import ValidationError


class TextFieldNotNull(ValidationError):
    """Поле text должно быть заполнено."""

    def __init__(self):
        self.message = {"text": "Поле text должно быть заполнено"}
        super().__init__(self.message)


class ConfirmationCodeError(ValidationError):
    """Неверный код подтверждения."""

    def __init__(self):
        self.message = {"confirmation_code": "Неверный код подтверждения!"}
        super().__init__(self.message)


class UserNameMeError(ValidationError):
    """Нельзя использовать me в качесте имени."""

    def __init__(self):
        self.message = {"username": "Нельзя использовать me в качесте имени!"}
        super().__init__(self.message)


class YearValidationError(ValidationError):
    """Год не должен быть больше текущего."""

    def __init__(self):
        self.message = {"year": "Год не должен быть больше текущего!"}
        super().__init__(self.message)


class ScoreValidationError(ValidationError):
    """Значение рейтинга должно быть целым числом от 0 до 10"""

    def __init__(self):
        self.message = {"score": "Значение рейтинга должно быть целым числом"
                                 " от 0 до 10"}
        super().__init__(self.message)


class ReviewUniqueExist(ValidationError):
    """Отзыв уже оставлен."""

    def __init__(self):
        self.message = {"detail": "Отзыв уже оставлен"}
        super().__init__(self.message)
