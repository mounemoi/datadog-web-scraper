import unittest
from mock import Mock
from mock import patch
import re

import web_scraping

class TestWebScraping(unittest.TestCase):
    def setUp(self):
        self.mock_log = Mock()
        web_scraping.WebScraping.log = self.mock_log

        self.mock_gauge = Mock()
        web_scraping.WebScraping.gauge = self.mock_gauge

        self.requests_patcher = patch('web_scraping.requests.get')
        self.mock_requests = self.requests_patcher.start()

        self.mock_content = Mock()

    def tearDown(self):
        self.requests_patcher.stop

    def setup_mock(self, content=None):
        self.mock_log.reset_mock()
        self.mock_gauge.reset_mock()
        self.mock_requests.reset_mock()
        self.mock_content.reset_mock()
        if content is not None:
            self.mock_content.content = content
            self.mock_requests.return_value = self.mock_content
        else:
            self.mock_requests.side_effect = Exception('fail')

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


    def assert_request_url(self, url):
        self.assertEqual(self.mock_requests.call_args[0][0], url)

    def assert_request_not_called(self):
        self.mock_requests.assert_not_called()


    def test_validation(self):
        ws = web_scraping.WebScraping()

        self.setup_mock()
        ws.check({})
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, 'skipping instance, no name found.')
        self.assert_request_not_called()
        self.assert_gauge_not_called()

        self.setup_mock()
        ws.check({ 'name' : 'test' })
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, 'skipping instance, no url found.')
        self.assert_request_not_called()
        self.assert_gauge_not_called()

        self.setup_mock()
        ws.check({ 'name' : 'test', 'url' : 'http://example.com' })
        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, 'skipping instance, no xpath found.')
        self.assert_request_not_called()
        self.assert_gauge_not_called()

    def test_invalid_url(self):
        name = 'test'
        url  = 'bad url'

        self.setup_mock()
        ws = web_scraping.WebScraping()
        ws.check({
            'name'  : name,
            'url'   : url,
            'xpath' : '',
        })

        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log_match(1, r'%s : failed to get website' % name)
        self.assert_request_url(url)
        self.assert_gauge_not_called()

    def test_invalid_value(self):
        name = 'test'
        url  = 'http://example.com'

        self.setup_mock('<div id="hoge">test</div>')
        ws = web_scraping.WebScraping()
        ws.check({
            'name'    : name,
            'url'     : url,
            'xpath'   : '//*[@id="hoge"]/text()',
        })

        self.assert_info_log_not_called()
        self.assert_error_log_count(1)
        self.assert_error_log(1, '%s : failed to get value (default value used) : could not convert string to float: ' % name)
        self.assert_request_url(url)
        self.assert_gauge_not_called()

    def test_success(self):
        name  = 'test'
        url   = 'http://example.com'
        value = '-100.1'

        self.setup_mock('<div id="hoge">test=%s</div>' % value)
        ws = web_scraping.WebScraping()
        ws.check({
            'name'  : name,
            'url'   : url,
            'xpath' : '//*[@id="hoge"]/text()',
        })

        self.assert_info_log_count(1)
        self.assert_info_log(1, '%s = %f' % (name, float(value)))
        self.assert_error_log_not_called()
        self.assert_request_url(url)
        self.assert_gauge(name, float(value))

    def test_default_value(self):
        name = 'test'
        url  = 'http://example.com'
        default_value = '100.2'

        self.setup_mock('<div id="hoge">test=-100.1</div>')
        ws = web_scraping.WebScraping()
        ws.check({
            'name'    : name,
            'url'     : url,
            'xpath'   : '//*[@id="fuga"]/text()',
            'default' : default_value,
        })

        self.assert_info_log_count(2)
        self.assert_info_log(1, '%s : failed to get value (default value used)' % name)
        self.assert_info_log(2, '%s = %f' % (name, float(default_value)))
        self.assert_error_log_not_called()
        self.assert_request_url(url)
        self.assert_gauge(name, float(default_value))

    def test_invalid_default_value(self):
        name = 'test'
        url  = 'http://example.com'
        default_value = 'invalid'

        self.setup_mock('<div id="hoge">test=-100.1</div>')
        ws = web_scraping.WebScraping()
        ws.check({
            'name'    : name,
            'url'     : url,
            'xpath'   : '//*[@id="fuga"]/text()',
            'default' : default_value,
        })

        self.assert_info_log_count(1)
        self.assert_info_log(1, '%s : failed to get value (default value used)' % name)
        self.assert_error_log_count(1)
        self.assert_error_log(1, '%s : invalid default value : could not convert string to float: %s' % (name, default_value))
        self.assert_request_url(url)
        self.assert_gauge_not_called()
