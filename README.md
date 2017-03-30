# datadog-web-scraper

This is a Agent Check that imports the value got by Web Scraping as [Datadog](https://www.datadoghq.com/)'s custom metrics.
By specifying the URL and XPath of the value you want to get, you can periodically import it into Datadog.

## Things to prepare

- Server on which [Datadog Agent](http://docs.datadoghq.com/guides/basic_agent_usage/) is installed

Install this Agent Check on this server.

## How to setup

This section describes how to install this Agent Check on Datadog Agent installed on CentOS.
Please read accordingly depending on the installation environment.

### 1. Install Python Module

Install Python Module required for this Agent Check in Python of datadog-agent.

```bash
$ sudo /opt/datadog-agent/embedded/bin/pip install lxml
```

### 2. Install this Agent Check

Place `./checks.d/web_scraping.py` in this repository in `/etc/dd-agent/checks.d/`.

```bash
$ sudo cp ./checks.d/web_scraping.py /etc/dd-agent/checks.d/
```

### 3. Place custom check configuration file

Create `/etc/dd-agent/conf.d/web_scraping.yaml` with reference to `./conf.d/web_scraping.yaml.example` in this repository.

```yaml
init_config:
   min_collection_interval: 60

instances:
   - name: wikipedia.en.page.count
     url: https://en.wikipedia.org/wiki/Main_Page
     xpath: //*[@id="articlecount"]/a[1]/text()
   - name: qiita.datadog.entry
     url: http://qiita.com/tags/Datadog
     xpath: //*[@id="main"]/div/div/div[1]/div[2]/div[1]/div[1]/text()
```

- `min_collection_interval` specifies the check interval (in seconds)
- `instances` specify information of the value you want to get
  - `name` : Custom metrics name of Datadog
  - `url` : URL of the value you want to get
  - `xpath` : XPath of the value you want to get
  - `default` : Default value when value can not be obtained from html (optional)

If the acquired value contains a value other than a numerical value, only the numerical value is extracted.

### 4. Test
You have completed the installation of Agent Check.
Please test with the following command.

```bash
$ sudo -u dd-agent dd-agent check web_scraping
```

The numerical value got by Agent Check will be displayed as a log, so please check.

### 5. Restart Datadog Agent
Finally restart Datadog Agent.

```bash
$ sudo /etc/init.d/datadog-agent restart
```

Your custom metrics should now be sent to Datadog.

# License

This software is released under the [MIT License](http://opensource.org/licenses/MIT), see LICENSE.

