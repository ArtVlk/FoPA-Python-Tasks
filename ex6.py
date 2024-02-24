import unittest


def merge(*iterables, key=None):
    merged = []
    for itarable in iterables:
        merged += list(itarable)
    if key:
        return iter(sorted(merged, key=key))
    return iter(sorted(merged))


def log_key(s):
    date = s[s.find('[')
             + 1:s.find(']',
                        s.find('['))]

    months = {"Jan": "01",
              "Feb": "02",
              "Mar": "03",
              "Apr": "04",
              "May": "05",
              "Jun": "06",
              "Jul": "07",
              "Aug": "08",
              "Sep": "09",
              "Oct": "10",
              "Nov": "11",
              "Dec": "12", }

    day = date[0:2]
    month = date[3:6]
    month = months[month]
    year = date[7:11]
    hour = date[12:14]
    minute = date[15:17]
    second = date[18:20]

    formatted_date = ("{0}{1}{2}{3}{4}{5}"
                      .format(year, month, day,
                              hour, minute, second))
    return formatted_date


class TestTest(unittest.TestCase):
    def test_generates_properly(self):
        assert '20120513063317' == log_key('1 [13/May/2012:06:33:17 +0600] ef')


class TestMerge(unittest.TestCase):
    def test_key(self):
        first = range(10)
        second = range(5)
        assert ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4]
                == list(merge(iter(first), iter(second))))

    def test_merge(self):
        ex1 = ' 127.0.0.1 - - [13/May/2012:06:33:17 +0600] "OPTIONS'
        ex2 = ' 127.0.0.1 - - [13/May/2012:06:33:17 +0600] "OPTIONS'
        ex3 = ' 192.168.74.24 - - [28/Jul/2012:13:11:27 +0600] "GET'
        ex4 = ' 192.168.12.9 - - [28/Jul/2012:13:11:40 +0600] "GET'
        ex5 = ' 192.168.12.9 - - [28/Jul/2012:13:11:40 +0600] "GET'
        h = merge(iter([ex1, ex4]), iter([ex5, ex2, ex3]), key=log_key)
        assert [ex1, ex2, ex3, ex4, ex5] == list(h)
