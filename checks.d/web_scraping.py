import requests
import re
from lxml import html
from checks import AgentCheck

class WebScraping(AgentCheck):
    def check(self, instance):

        for param in ['name', 'url', 'xpath']:
            if param not in instance:
                self.log.error('skipping instance, no %s found.' % param)
                return

        name = instance['name']

        try:
            page = requests.get(instance['url'], timeout = 10)
            contents = html.fromstring(page.content).xpath(instance['xpath'])
        except Exception as e:
            self.log.error('%s : %s' % (name, str(e)))
            return

        value_text = ''
        if len(contents) >= 1:
            try:
                value_text = re.sub(r'[^0-9]+', '', contents[0])
            except Exception as e:
                self.log.error('%s : %s' % (name, str(e)))
                return
        if not value_text.isdigit():
            if 'default' in instance:
                value_text = instance['default']
            else:
                return
        value = int(value_text)

        self.log.info('%s = %d' % (name, value))
        self.gauge(name, value)

