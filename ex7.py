from functools import wraps


def get_gift(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print('Я молодец! Я заслужил +1 балл!')
        return fn(*args, **kwargs)

    return wrapper


@get_gift
def last_func():
    print('Ура, на сегодня всё! Спасибо за внимание!')


last_func()