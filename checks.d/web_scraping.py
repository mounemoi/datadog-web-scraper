import requests
import re
import lxml.html
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
        except Exception as e:
            self.log.error('%s : failed to get website : %s' % (name, str(e)))
            return

        value = None
        try:
            contents = lxml.html.fromstring(page.content).xpath(instance['xpath'])
            if len(contents) >= 1 and isinstance(contents[0], str):
                value_text = re.sub(r'[^\-\.0-9]+', '', contents[0])
                value = float(value_text)
            else:
                self.log.info('%s : failed to get value (default value used)' % name)
        except Exception as e:
            self.log.error('%s : failed to get value (default value used) : %s' % (name, str(e)))

        if value is None:
            if 'default' in instance:
                try:
                    value = float(instance['default'])
                except Exception as e:
                    self.log.error('%s : invalid default value : %s' % (name, str(e)))
                    return
            else:
                return

        self.log.info('%s = %f' % (name, value))
        self.gauge(name, value)

