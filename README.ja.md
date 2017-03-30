# datadog-web-scraper

Web Scraping で取得した値を [DataDog](http://datadoghq.com) のカスタムメトリクスとして取り込む Agent Check です。
取得したい値の URL と XPath を指定することで、Datadog に定期的に取り込むことができます。

## 用意するもの

- [Datadog Agent](http://docs.datadoghq.com/ja/guides/basic_agent_usage/) をインストールしたサーバ

このサーバに、この Agent Check をインストールします。

## セットアップ方法

ここでは、CentOS にインストールした Datadog Agent に、この Agent Check をインストールする方法を記載します。
インストール環境によって適宜読み替えてください。

### 1. Python Module のインストール

この Agent Check で必要となる Python Module を datadog-agent の Python にインストールします。

```bash
$ sudo /opt/datadog-agent/embedded/bin/pip install lxml
```

### 2. Agent Check のインストール

このリポジトリの `./checks.d/web_scraping.py` を `/etc/dd-agent/checks.d/` に配置します。

```bash
$ sudo cp ./checks.d/web_scraping.py /etc/dd-agent/checks.d/
```

### 3. Agent Check の設定ファイルの配置

このリポジトリの `./conf.d/web_scraping.yaml.example` を参考に `/etc/dd-agent/conf.d/web_scraping.yaml` を作成します
。

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

- `min_collection_interval` にはチェック間隔（秒数）を指定します
- `instances` に取得したい値の情報を指定します
  - `name` : Datadog のカスタムメトリクス名
  - `url` : 取得したい値の URL
  - `xpath` : 取得したい値の XPath
  - `default` : 値が html から取得できなかった際のデフォルト値 (optional)

取得した値に数値以外が含まれる場合には、数値のみが抽出されます。

### 4. 動作確認
以上で Agent Check のインストールは完了です。
以下のコマンドで値が取得できているか試してみましょう。

```bash
$ sudo -u dd-agent dd-agent check web_scraping
```

取得した数値がログとして表示されますので、意図通り取得できていることを確認しましょう。

### 5. Datadog Agent の再起動
最後に Datadog Agent を再起動します。

```bash
$ sudo /etc/init.d/datadog-agent restart
```

これで、Datadog にカスタムメトリクスが送信されているはずです。

# ライセンス

このプログラムは [MIT License](http://opensource.org/licenses/MIT) にて提供されます。LICENSE を参照してください。

