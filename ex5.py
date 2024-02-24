from collections import Counter, defaultdict
from datetime import datetime
import unittest


class make_stat():
    def __init__(self):
        self.log_data = []

    def add_line(self, line):
        blocks = line.split(' ')
        if len(blocks) < 12 or not blocks[3].startswith('[') or not blocks[4].endswith(']'):
            return

        user = blocks[0]
        timestamp_str = blocks[3] + blocks[4]
        try:
            timepoints = (datetime.
                          strptime(timestamp_str, "[%d/%b/%Y:%H:%M:%S%z]"))
        except ValueError:
            return

        resource = blocks[6]
        user_data = " ".join(blocks[11:-1])
        response_time = blocks[-1]

        self.log_data.append({
            'user': user,
            'user_data': user_data,
            'timepoints': timepoints,
            'resource': resource,
            'response_time': response_time
        })

    def most_user(self):
        if not self.log_data:
            return None

        users = Counter(entry['user'] for entry in self.log_data)
        if users:
            most_active_client = users.most_common(1)[0][0]
            return most_active_client
        else:
            return None

    def most_user_day(self):
        if not self.log_data:
            return None

        active_clients_by_day = {}

        for log_entry in self.log_data:
            entry_date = log_entry['timepoints'].date()

            if entry_date in active_clients_by_day:
                active_clients_by_day[entry_date].append(log_entry['user'])
            else:
                active_clients_by_day[entry_date] = [log_entry['user']]

        most_user_day = {}

        for date, clients in active_clients_by_day.items():
            most_common_client = max(set(clients), key=clients.count)
            most_user_day[date] = most_common_client

        return most_user_day if most_user_day else None


    def most_page(self):
        if not self.log_data:
            return None

        resources = Counter(entry['resource'] for entry in self.log_data)
        if resources:
            most_resource = resources.most_common(1)[0][0]
            return most_resource
        else:
            return None

    def most_browser(self):
        if not self.log_data:
            return None

        browsers = defaultdict(int)

        for log_entry in self.log_data:
            browser = log_entry['user_data']
            browsers[browser] += 1

        if browsers:
            most_popular_browser = max(browsers, key=browsers.get)
            return most_popular_browser.replace('"', '')
        else:
            return None

    def fastest_page(self):
        if not self.log_data:
            return None

        fastest_response_time = float('inf')
        fastest_page = None

        for log_entry in self.log_data:
            response_time = int(log_entry['response_time'])
            if response_time < fastest_response_time:
                fastest_response_time = response_time
                fastest_page = log_entry['resource']

        return fastest_page


    def slowest_page_load(self):
        if not self.log_data:
            return None

        page_load_times = defaultdict(list)

        for log_entry in self.log_data:
            (page_load_times[log_entry['resource']]
             .append(int(log_entry['response_time'])))

        average_page_load_times = {page: sum(times) / len(times)
                                   for page, times in page_load_times.items()}

        if average_page_load_times:
            slowest_page = max(average_page_load_times,
                               key=average_page_load_times.get)
            return slowest_page
        else:
            return None


    def slowest_page(self):
        if not self.log_data:
            return None

        page_load_times = {}

        for log_entry in self.log_data:
            resource = log_entry['resource']
            response_time = int(log_entry['response_time'])

            if resource in page_load_times:
                page_load_times[resource].append(response_time)
            else:
                page_load_times[resource] = [response_time]
        average_page_load = {page: sum(times) / len(times)
                             for page, times in page_load_times.items()}

        slowest_page = max(average_page_load, key=average_page_load.get)

        return slowest_page

    def results(self):
        result = {
            'FastestPage': self.fastest_page(),
            'MostActiveClient': self.most_user(),
            'MostActiveClientByDay':
                self.most_user_day(),
            'MostPopularBrowser': self.most_browser(),
            'MostPopularPage': self.most_page(),
            'SlowestAveragePage':
                self.slowest_page_load(),
            'SlowestPage': self.slowest_page()
        }
        return result


class LogStatTests(unittest.TestCase):
    def setUp(self):
        self.stat = make_stat()
        test_data = [
            '192.168.74.6 - '
            '- [13/May/2012:06:33:18 +0600] '
            '"GET /img/team_green.png HTTP/1.1" '
            '304 190 '
            '"http://callider/menu-top.php" '
            '"Mozilla/5.0 (compatible; MSIE 9.0; '
            'Windows NT 6.1; WOW64; Trident/5.0)" '
            '1786',
            '192.168.74.6 - '
            '- [13/May/2012:06:33:18 +0600] '
            '"GET /img/notification.png HTTP/1.1" '
            '304 189 '
            '"http://callider/menu-top.php" '
            '"Mozilla/5.0 (compatible; '
            'MSIE 9.0; Windows NT 6.1; '
            'WOW64; Trident/5.0)" 546',
            '192.168.253.239 - '
            '- [13/May/2012:06:33:28 +0600] '
            '"GET /menu-top.php HTTP/1.1" '
            '200 2081 "-" "Mozilla/4.0 '
            '(compatible; MSIE 7.0; '
            'Windows NT 6.1; WOW64; '
            'Trident/5.0; SLCC2; '
            '.NET CLR 2.0.50727; '
            '.NET CLR 3.5.30729; '
            '.NET CLR 3.0.30729; '
            'Media Center PC 6.0; '
            'InfoPath.3; .NET4.0C; '
            '.NET4.0E; MS-RTC LM 8; '
            'AskTbCLM/5.15.1.22229; '
            'BOIE9;RURU)" '
            '35654'
        ]
        for line in test_data:
            self.stat.add_line(line)

    def test_most_user(self):
        self.assertEqual(self.stat.most_user(),
                         '192.168.74.6')

    def test_most_user_day(self):
        expected_result = {
            datetime(2012, 5, 13).date(): '192.168.74.6'
        }
        self.assertEqual(self.stat.most_user_day(),
                         expected_result)

    def test_most_page(self):
        self.assertEqual(self.stat.most_page(),
                         '/img/team_green.png')

    def test_most_browser(self):
        self.assertEqual(self.stat.most_browser(),
                         'Mozilla/5.0 '
                         '(compatible; MSIE 9.0; '
                         'Windows NT 6.1; '
                         'WOW64; '
                         'Trident/5.0)')

    def test_fastest_page(self):
        self.assertEqual(self.stat.fastest_page(),
                         '/img/notification.png')

    def test_slowest_page_load(self):
        self.assertEqual(self.stat.slowest_page_load(),
                         '/menu-top.php')

    def test_slowest_page(self):
        self.assertEqual(self.stat.slowest_page(),
                         '/menu-top.php')


if __name__ == '__main__':
    unittest.main()
