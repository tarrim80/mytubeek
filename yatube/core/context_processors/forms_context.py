def forms_message_context(request) -> dict:
    if request.path == '/auth/password_reset/done/':
        return {
            'form_title': 'Сброс пароля прошел успешно',
            'form_header': 'Отправлено письмо',
            'form_body': '''Проверьте свою почту, вам должно прийти
                            письмо со ссылкой для восстановления пароля''',
        }
    elif request.path == '/auth/logout/':
        return {
            'form_title': 'Вы вышли из системы',
            'form_header': 'Выход',
            'form_body': 'Вы вышли из своей учётной записи. Ждем Вас снова',
        }
    elif request.path == '/auth/password_change/done/':
        return {
            'form_title': 'Пароль изменён',
            'form_header': 'Пароль изменён',
            'form_body': 'Пароль изменён успешно',
        }
    elif request.path == '/auth/reset/done/':
        return {
            'form_title': 'Сброс пароля прошел успешно',
            'form_header': 'Восстановление пароля завершено',
            'form_body': 'Ваш пароль был сохранен. Используйте его для входа',
            'form_href_text': 'Войти',
            'form_href': '/auth/login',
        }
    return {}


def forms_input_context(request):
    return {}
