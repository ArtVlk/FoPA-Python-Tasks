#!/usr/bin/env python

import sys


def f0():
    return 10 / 0


def f1():
    d = {}
    return d['key']


def f2():
    return 0/0


def f3():
    try:
        result = 1.0/0.0
    except FloatingPointError:
        print("Unable to perform the operation. The result is too large.")
    else:
        print(result)
def f4():
    import math
    return math.exp(1000)


def f5():
    return 0/0


def f6():
    assert True*True*False


def f7():
    class A:
        pass
    a = A()
    a.x


def f8():
    f = open('non_existent.txt')


def f9():
    import imposter


def f10():
    d = {'key': 'value'}
    return d['word']


def f11():
    arr = [1, 2, 3]
    return arr[3]


def f12():
    d = {'key' : 'word'}
    return d['k_key']


def f13():
    return x


def f14():
    return eval('x === 5')


def f15():
   return int('abc')


def f16():
    return b'\x80abc'.decode('utf-8')


def check_exception(f, exception):
    try:
        f()
    except exception:
        pass
    else:
        print("Bad luck, no exception caught: %s" % exception)
        sys.exit(1)


check_exception(f0, BaseException)
check_exception(f1, Exception)
check_exception(f2, ArithmeticError)
check_exception(f3, FloatingPointError)
check_exception(f4, OverflowError)
check_exception(f5, ZeroDivisionError)
check_exception(f6, AssertionError)
check_exception(f7, AttributeError)
check_exception(f8, EnvironmentError)
check_exception(f9, ImportError)
check_exception(f10, LookupError)
check_exception(f11, IndexError)
check_exception(f12, KeyError)
check_exception(f13, NameError)
check_exception(f14, SyntaxError)
check_exception(f15, ValueError)
check_exception(f16, UnicodeError)

print("Congratulations, you made it!")
