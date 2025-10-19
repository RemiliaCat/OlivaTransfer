import requests as req
import xml.etree.ElementTree as ET

class RSSapi(object):
    '''
    A simple RSS feed fetcher and parser unity, which can fetch RSS feeds from multiple sources, 
    parse them, and store the latest GUIDs to avoid duplicate processing.

    methods:
    - fetch(rss_source=None): Fetch RSS feeds from the configured sources, or passed sources.
    - parse(): Parse the fetched RSS feeds and extract items.
    - update(rss_source=None, target=None): Update the RSS sources or targets.
    - export(data=True, rss_source=False, target=False, guids=False): Export current configuration and data.

    attributes:
    - rss_source: A dict of platform names to RSS feed URLs.
    - target: A dict defining where to push the parsed RSS items.
    - guids: A dict storing the latest processed GUIDs for each platform to avoid duplicates.
    - data_raw: Raw fetched RSS feed data.
    - data: Parsed RSS feed items.
    '''
    def __init__(self, rss_source: dict = None, target: dict = None, guids: dict = {}):
        '''
        :param rss_source: 
            A dict of platform names to RSS feed URLs, 
            e.g. {"platform1": "http://example.com/rss1", "platform2": "http://example.com/rss2"}
        :param target: 
            A dict defining where to push the parsed RSS items, 
            e.g. {"platform1": {"groups": [...], "users": [...]}, ...}
        :param guids: 
            A dict storing the latest processed GUIDs for each platform to avoid duplicates,
            could be reloaded from local storage, such as 'plugin/data/OlivaTransfer/guids.json'
        '''
        self.rss_source = rss_source
        self.target = target
        self.guids = guids
        self.data_raw = None
        self.data = None

    def fetch(self, rss_source: dict = None):
        '''
        Fetch RSS feeds from the configured sources, or the passed sources.
        '''
        if rss_source is None:
            rss_source = self.rss_source
        if rss_source is None or len(rss_source) == 0:
            return None
        tmp_rss = {}
        for platform, url in rss_source.items():
            if rss_source[platform] != "":
                print(f'fetching RSS from {url}...')
                response = self._request(url)
                if response.status_code == 200:
                    print('request success')
                    tmp_rss[platform] = response.text
                else:
                    print(f'request failed with status code {response.status_code}')
        self.data_raw = tmp_rss
        return tmp_rss

    def parse(self):
        '''
        Parse the fetched RSS feeds and extract items.
        '''
        if self.data_raw is None or len(self.data_raw) == 0:
            return None
        tmp_data = {}
        for platform, raw in self.data_raw.items():
            if self.guids(platform) is None:
                self.guids[platform] = ''
            root = ET.fromstring(raw)
            items = []
            for item in root.findall('.//item'):
                if item.find('guid') in self.guids[platform]:
                    continue
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                guid = item.find('guid').text if item.find('guid') is not None else ''
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                items.append({
                    'title': title,
                    'link': link,
                    'guid': guid,
                    'pubDate': pubDate,
                    'description': description
                })
                self.guids[platform] = guid
            tmp_data[platform] = items
        self.data = tmp_data
        return tmp_data
        
    def update(self, rss_source:dict=None, target:dict=None):
        '''
        Update the RSS sources or targets.
        :param rss_source: A dict of platform names to RSS feed URLs.
        :param target: A dict defining where to push the parsed RSS items.
        '''
        if rss_source is not None:
            self.rss_source = rss_source
        if target is not None:
            self.target = target
        return
    
    def export(self, data: bool = True ,rss_source: bool = False, target: bool = False, guids: bool = False):
        '''
        Export current configuration, return a dict like:
        {
            "data": {...}
            "rss_source": {...},
            "target": {...},
            "guids": {...}
        }
        :param data: whether to include parsed data in the output
        :param rss_source: whether to include rss_source in the output
        :param target: whether to include target in the output
        :param guids: whether to include guids in the output
        '''
        tmp_dict = {}
        if data:
            tmp_dict["data"] = self.data
        if rss_source:
            tmp_dict["rss_source"] = self.rss_source
        if target:
            tmp_dict["target"] = self.target
        if guids:
            tmp_dict["guids"] = self.guids
        return tmp_dict
    
    def _request(self, url: str, method: str = "GET"):
        # session = req.Session()
        # retries = req.adapters.Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504], allowed_methods=["POST", "GET"])
        # session.mount('https://', req.adapters.HTTPAdapter(max_retries=retries))
        # session.mount('http://', req.adapters.HTTPAdapter(max_retries=retries))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        # response = session.get(url, headers=headers, timeout=5)
        response = req.request(method='GET', url=url, headers=headers, timeout=10)
        return response

if __name__ == "__main__":
    rss_api = RSSapi(
        rss_source={
            "bilibili_2267573": "https://rsshub.rssforever.com/bilibili/user/video/361737204"
        },
        target={
            "qq": {
                "groups": ["group1", "group2"],
                "users": ["user1", "user2"]
            }
        }
    )
    rss_api.fetch()
    rss_api.parse()
    print(rss_api.export(data=True, rss_source=True, target=True, guids=True))