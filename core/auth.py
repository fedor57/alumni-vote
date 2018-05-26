# coding=utf-8
import requests


def get_data(auth_code):
    """ Метод получающий данные из сервиса авторизации"""
    r = requests.post("http://auth.alumni57.ru/api/v1/check_code", data={'code': auth_code})
    data = r.json()
    if data['status'] == 'ok':
        data['status'] = 'valid'
    if data['status'] == 'disabled' or data['status'] == 'banned':
        data['status'] = 'revoked'
    return data


def get_temporary_code(auth_code, app):
    r = requests.post("http://auth.alumni57.ru/api/v1/get_app_code",
                      data={
                          'code': auth_code,
                          'app': app
                      })
    return r.json()
