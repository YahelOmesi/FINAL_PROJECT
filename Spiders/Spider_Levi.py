import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os
import re

# הגדרת המקטעים של צוואת לוי
LEVI_CONFIG = {
    '4Q213_4QLevi_a': '44406001',
    '4Q213a_4QLevi_b': '44406002',
    '4Q213b_4QLevi_c': '44406003',
    '4Q214_4QLevi_d': '44406004',
    '4Q214a_4QLevi_e': '44406005',
    '4Q214b_4QLevi_f': '44406006',
    '1Q21_1QTLevi': '44406021'
}

# פונקציה לטעינת ה-URLs שכבר הורדו כדי למנוע כפילויות ולעצור/להמשיך
def load_already_downloaded_urls():
    file_path = os.path.join('..', 'Data', 'Data_Levi', 'Levi_All.json')
    if not os.path.exists(file_path):
        return set()
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            return {item['url'] for item in data if isinstance(item, dict) and 'url' in item}
        except:
            return set()

def parse_word(response):
    word = response.meta['word']
    pos_tags = response.xpath('//pos//text()').getall()
    bin_tags = response.xpath('//span[@class="bin"]//text()').getall()
    all_grammar_tags = [t.strip() for t in pos_tags + bin_tags if t.strip()]
    
    if all_grammar_tags:
        word['lexicon_0'] = " ".join(all_grammar_tags)
    else:
        word['lexicon_0'] = None
        
    for i in range(1, 5):
        lex = response.xpath(f'//body/hr[{i}]/following-sibling::text()').get()
        word[f'lexicon_{i}'] = lex.strip() if lex and lex.strip() != '' else None

    translation_list = response.xpath('//span[@class="mgT"]/text()').getall()
    if translation_list:
        cleaned = [t.strip() for t in translation_list if t.strip() and not re.match(r'^\d+$', t)]
        for i in range(4):
            word[f'meaning_{i}'] = cleaned[i] if i < len(cleaned) else None
    
    split_words = response.xpath('//span[@class="lem"]//text()').getall()
    split_words = [w.strip() for w in split_words if w.strip()]
    for i in range(4):
        word[f'split_word_{i}'] = split_words[i] if i < len(split_words) else None

    yield word

class LeviSpider(scrapy.Spider):
    name = 'levi_spider'
    
    def start_requests(self):
        self.downloaded_urls = load_already_downloaded_urls()
        for name, code in LEVI_CONFIG.items():
            url = f"https://cal.huc.edu/get_a_chapter.php?file={code}"
            yield scrapy.Request(url, meta={'scroll_name': name})

    def parse(self, response):
        scroll_name = response.meta['scroll_name']
        for el in response.css('tr > td:nth-child(2) > a'):
            url = el.xpath('@href').get()
            if url in self.downloaded_urls:
                continue
                
            word = {'text': el.css('::text').get(), 'url': url, 'scroll_name': scroll_name}
            yield scrapy.Request(
                url=f"https://cal.huc.edu/{url}", 
                meta={'word': word}, 
                callback=parse_word
            )

class SingleJsonWriterPipeline:
    def open_spider(self, spider):
        self.output_dir = os.path.join('..', 'Data', 'Data_Levi')
        os.makedirs(self.output_dir, exist_ok=True)
        self.file_path = os.path.join(self.output_dir, 'Levi_All.json')
        # פתיחה ב-append אם הקובץ קיים, כדי להוסיף עליו
        file_exists = os.path.exists(self.file_path)
        self.file = open(self.file_path, 'a' if file_exists else 'w', encoding='utf-8')
        if not file_exists:
            self.file.write('[\n')
        self.first_item = not file_exists

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        self.first_item = False
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'ITEM_PIPELINES': {'__main__.SingleJsonWriterPipeline': 1},
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(LeviSpider)
    process.start()