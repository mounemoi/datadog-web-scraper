import unittest
from mock import Mock
from mock import patch
import re

import web_scraping

class TestWebScraping(unittest.TestCase):
    def reset_mock(self):
        if not hasattr(self, 'log'):
            self.mock_log = Mock()
            web_scraping.WebScraping.log = self.mock_log
        else:
            self.mock_log.reset_mock()

        if not hasattr(self, 'gauge'):
            self.mock_gauge = Mock()
            web_scraping.WebScraping.gauge = self.mock_gauge
        else:
            self.mock_gauge.reset_mock()


    def get_info_log(self, order):
        return self.mock_log.info.call_args_list[order - 1][0][0]

    def assert_info_log(self, order, string):
        self.assertEqual(self.get_info_log(order), string)

    def assert_info_log_match(self, order, match):
        self.assertTrue(re.match(match, self.get_info_log(order)))

    def assert_info_log_count(self, order):
        self.assertEqual(len(self.mock_log.info.call_args_list), order)

    def assert_info_log_not_called(self):
        self.mock_log.info.assert_not_called()


    def get_error_log(self, order):
        return self.mock_log.error.call_args_list[order - 1][0][0]

    def assert_error_log(self, order, string):
        self.assertEqual(self.get_error_log(order), string)

    def assert_error_log_match(self, order, match):
        self.assertTrue(re.match(match, self.get_error_log(order)))

    def assert_error_log_count(self, order):
        self.assertEqual(len(self.mock_log.error.call_args_list), order)

    def assert_error_log_not_called(self):
        self.mock_log.error.assert_not_called()


    def assert_gauge(self, name, num):
        self.mock_gauge.assert_called_with(name, num)

    def assert_gauge_not_called(self):
        self.mock_gauge.assert_not_called()


    def test_validation(self):
        ws = web_scraping.WebScraping()

        self.reset_mock()
        ws.check({})
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, 'skipping instance, no name found.')
        self.assert_gauge_not_called()

        self.reset_mock()
        ws.check({ 'name' : 'test' })
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, 'skipping instance, no url found.')
        self.assert_gauge_not_called()

        self.reset_mock()
        ws.check({ 'name' : 'test', 'url' : 'http://example.com' })
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, 'skipping instance, no xpath found.')
        self.assert_gauge_not_called()

    def test_invalid_url(self):
        self.reset_mock()

        ws = web_scraping.WebScraping()

        ws.check({
            'name'  : 'test',
            'url'   : '',
            'xpath' : '',
        })

        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log_match(1, r'test : failed to get website')
        self.assert_gauge_not_called()

    @patch('web_scraping.requests.get')
    def test_invalid_value(self, mock):
        self.reset_mock()

        mock_page = Mock()
        mock_page.content = '<div id="hoge">test</div>'
        mock.return_value = mock_page

        name = 'test'
        url = 'http://example.com'
        ws = web_scraping.WebScraping()
        ws.check({
            'name'    : name,
            'url'     : url,
            'xpath'   : '//*[@id="hoge"]/text()',
        })

        self.assertEqual(mock.call_args[0][0], url)
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, '%s : failed to get value (default value used) : could not convert string to float: ' % name)
        self.assert_gauge_not_called()

    @patch('web_scraping.requests.get')
    def test_success(self, mock):
        self.reset_mock()

        mock_page = Mock()
        value = '-100.1'
        mock_page.content = '<div id="hoge">test=%s</div>' % value
        mock.return_value = mock_page

        name = 'test'
        url = 'http://example.com'
        ws = web_scraping.WebScraping()
        ws.check({
            'name'  : name,
            'url'   : url,
            'xpath' : '//*[@id="hoge"]/text()',
        })

        self.assertEqual(mock.call_args[0][0], url)
        self.assert_info_log_count(1)
        self.assert_info_log(1, '%s = %f' % (name, float(value)))
        self.assert_error_log_not_called()
        self.assert_gauge(name, float(value))

    @patch('web_scraping.requests.get')
    def test_default_value(self, mock):
        self.reset_mock()

        mock_page = Mock()
        mock_page.content = '<div id="hoge">test=-100.1</div>'
        mock.return_value = mock_page

        name = 'test'
        url = 'http://example.com'
        ws = web_scraping.WebScraping()
        default_value = '100.2'
        ws.check({
            'name'    : name,
            'url'     : url,
            'xpath'   : '//*[@id="fuga"]/text()',
            'default' : default_value,
        })

        self.assertEqual(mock.call_args[0][0], url)
        self.assert_info_log_count(2)
        self.assert_info_log(1, '%s : failed to get value (default value used)' % name)
        self.assert_info_log(2, '%s = %f' % (name, float(default_value)))
        self.assert_error_log_not_called()
        self.assert_gauge(name, float(default_value))

    @patch('web_scraping.requests.get')
    def test_invalid_default_value(self, mock):
        self.reset_mock()

        mock_page = Mock()
        mock_page.content = '<div id="hoge">test=-100.1</div>'
        mock.return_value = mock_page

        name = 'test'
        url = 'http://example.com'
        ws = web_scraping.WebScraping()
        ws.check({
            'name'    : name,
            'url'     : url,
            'xpath'   : '//*[@id="fuga"]/text()',
            'default' : 'invalid',
        })

        self.assertEqual(mock.call_args[0][0], url)
        self.assert_info_log_count(1)
        self.assert_info_log(1, '%s : failed to get value (default value used)' % name)
        self.assert_error_log_count(1)
        self.assert_error_log(1, '%s : invalid default value : could not convert string to float: invalid' % name)
        self.assert_gauge_not_called()
