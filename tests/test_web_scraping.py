import unittest
from mock import Mock
from mock import patch
import re

import web_scraping

class TestWebScraping(unittest.TestCase):
    def test_validation(self):
        mock_log = Mock()
        web_scraping.WebScraping.log = mock_log

        ws = web_scraping.WebScraping()

        ws.check({})
        mock_log.error.assert_called_with('skipping instance, no name found.')

        ws.check({ 'name' : 'test' })
        mock_log.error.assert_called_with('skipping instance, no url found.')

        ws.check({ 'name' : 'test', 'url' : 'http://example.com' })
        mock_log.error.assert_called_with('skipping instance, no xpath found.')

    def test_invalid_url(self):
        mock_log = Mock()
        web_scraping.WebScraping.log = mock_log

        ws = web_scraping.WebScraping()
        ws.check({
            'name'  : 'test',
            'url'   : '',
            'xpath' : '',
        })

        mock_log.error.assert_called_once()
        log_str = mock_log.error.call_args[0][0]
        self.assertTrue(re.match(r'test : failed to get website', log_str))

    @patch('web_scraping.requests.get')
    def test_invalid_value(self, mock):
        mock_log = Mock()
        web_scraping.WebScraping.log = mock_log

        mock_gauge = Mock()
        web_scraping.WebScraping.gauge = mock_gauge

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
        self.assertEqual(mock_log.error.call_args_list[0][0][0], '%s : failed to get value (default value used) : could not convert string to float: ' % name)
        mock_log.info.assert_not_called()
        mock_gauge.assert_not_called()

    @patch('web_scraping.requests.get')
    def test_success(self, mock):
        mock_log = Mock()
        web_scraping.WebScraping.log = mock_log

        mock_gauge = Mock()
        web_scraping.WebScraping.gauge = mock_gauge

        mock_page = Mock()
        mock_page.content = '<div id="hoge">test=-100.1</div>'
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
        mock_log.error.assert_not_called()
        mock_log.info.assert_called_with('%s = -100.100000' % name)
        mock_gauge.assert_called_with(name, -100.100000)

    @patch('web_scraping.requests.get')
    def test_default_value(self, mock):
        mock_log = Mock()
        web_scraping.WebScraping.log = mock_log

        mock_gauge = Mock()
        web_scraping.WebScraping.gauge = mock_gauge

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
            'default' : 100,
        })

        self.assertEqual(mock.call_args[0][0], url)
        mock_log.error.assert_not_called()
        self.assertEqual(mock_log.info.call_args_list[0][0][0], '%s : failed to get value (default value used)' % name)
        self.assertEqual(mock_log.info.call_args_list[1][0][0], '%s = 100.000000' % name)
        mock_gauge.assert_called_with(name, 100.000000)

    @patch('web_scraping.requests.get')
    def test_invalid_default_value(self, mock):
        mock_log = Mock()
        web_scraping.WebScraping.log = mock_log

        mock_gauge = Mock()
        web_scraping.WebScraping.gauge = mock_gauge

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
        self.assertEqual(mock_log.info.call_args_list[0][0][0], '%s : failed to get value (default value used)' % name)
        self.assertEqual(mock_log.error.call_args_list[0][0][0], '%s : invalid default value : could not convert string to float: invalid' % name)
        mock_gauge.assert_not_called()
