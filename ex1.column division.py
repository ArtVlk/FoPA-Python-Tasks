#!/usr/bin/env python3


def long_division(dividend, divider):
    '''
        Вернуть строку с процедурой деления «уголком» чисел dividend и divider.
        Формат вывода приведён на примерах ниже.

        Примеры:
        #>>> 12345÷25
        12345|25
        100  |493
         234
         225
           95
           75
           20

        #>>> 1234÷1423
        1234|1423
        1234|0

        #>>> 24600÷123
        24600|123
        246  |200
          0

        #>>> 246001÷123
        246001|123
        246   |2000
             1
        '''
    # INSERT CODE HERE
    numbers = list(map(int, str(dividend)))
    firstDividend = True
    print("  {}|{}".format(dividend, divider))

    offset, currentDividend = 0, 0

    while numbers:
        currentDividend = currentDividend * 10 + numbers.pop(0)
        if currentDividend >= divider:
            if offset:
                print("{:>{}}  {}".format('', offset, currentDividend))
            lenCurrentDividend = len(str(currentDividend))
            quotient = currentDividend // divider
            currentDividend = currentDividend % divider
            if firstDividend == 0:
                print("{:<{}}  {:>{}}".format('', offset, quotient * divider, len(str(currentDividend))))
            else:
                print('  ', quotient * divider, " " * (len(numbers)), "│", dividend // divider, sep="")
                firstDividend = False
            offset += lenCurrentDividend - len(str(currentDividend)) + (0 if currentDividend else 1)
    if not firstDividend:
        print("{:<{}}  {}".format('', offset, currentDividend))
    else:
        lenCurrentDividend = len(str(currentDividend))
        quotient = currentDividend // divider
        currentDividend = currentDividend % divider
        print('  ', dividend, " " * (len(numbers)), "│", dividend // divider, sep="")


def main():
    print(long_division(123, 123))
    print()
    print(long_division(1, 1))
    print()
    print(long_division(15, 3))
    print()
    print(long_division(3, 15))
    print()
    print(long_division(12345, 25))
    print()
    print(long_division(1234, 1423))
    print()
    print(long_division(87654532, 1))
    print()
    print(long_division(24600, 123))
    print()
    print(long_division(4567, 1234567))
    print()
    print(long_division(246001, 123))
    print()
    print(long_division(100000, 50))
    print()
    print(long_division(123456789, 531))
    print()
    print(long_division(425934261694251, 12345678))


if __name__ == '__main__':
    main()
