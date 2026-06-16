import scrapy
from scrapy.crawler import CrawlerProcess
import json

# הגדרת המגילות והקודים שלהן מהאתר
SCROLLS_CONFIG = {
    '1QapGen_Genesis_Apocryphon': {'base_code': '44404', 'range': 23}, 
    '11QtgJob_Job_Scroll': {'base_code': '44001', 'range': 39}         
}

def parse_word(response):
    word = response.meta['word']
    
    # 1. חילוץ התגיות הדקדוקיות
    pos_tags = response.xpath('//pos//text()').getall()
    bin_tags = response.xpath('//span[@class="bin"]//text()').getall()
    all_grammar_tags = [t.strip() for t in pos_tags + bin_tags if t.strip()]
    
    if all_grammar_tags:
        word['lexicon_0'] = " ".join(all_grammar_tags)
    else:
        word['lexicon_0'] = None
        
    for i in range(1, 5):
        word[f'lexicon_{i}'] = None

    # 2. חילוץ שורש
    split_words = response.xpath('//span[@class="lem"]//text()').getall()
    split_words = [w.strip() for w in split_words if w.strip()] 
    for i in range(4):
        word[f'split_word_{i}'] = split_words[i] if i < len(split_words) else None

    # 3. חילוץ משמעויות
    meanings = response.xpath('//span[contains(@class, "mgP") or contains(@class, "mg1")]//text()').getall()
    meanings = [m.strip() for m in meanings if m.strip() and not m.strip().isnumeric()] 
    for i in range(4):
        word[f'meaning_{i}'] = meanings[i] if i < len(meanings) else None

    yield word

class ScrollsWordSpider(scrapy.Spider):
    name = 'scrolls_spider'

    def start_requests(self):
        for name, config in SCROLLS_CONFIG.items():
            for i in range(1, config['range']):
                url = f"https://cal.huc.edu/get_a_chapter.php?file={config['base_code']}{i:02d}"
                yield scrapy.Request(url, meta={'scroll_name': name})

    def parse(self, response):
        scroll_name = response.meta['scroll_name']
        for el in response.css('tr > td:nth-child(2) > a'):
            word = {
                'text': el.css('::text').get(),
                'url': el.xpath('@href').get(),
                'scroll_name': scroll_name 
            }
            yield scrapy.Request(
                url=f"https://cal.huc.edu/{word['url']}",
                meta={'word': word},
                callback=parse_word
            )

# --- הפתרון שלנו: מנגנון שמירה ישירה (Pipeline) חסין תקלות ---
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.files = {}
        self.is_first_item = {}

    def process_item(self, item, spider):
        name = item['scroll_name']
        # פתיחת קובץ חדש למגילה אם עדיין לא קיים
        if name not in self.files:
            self.files[name] = open(f'{name}.json', 'w', encoding='utf-8')
            self.files[name].write('[\n')
            self.is_first_item[name] = True
        else:
            self.files[name].write(',\n')
        
        # המרת המילה ל-JSON ושמירה
        line = json.dumps(dict(item), ensure_ascii=False)
        self.files[name].write(line)
        return item

    def close_spider(self, spider):
        # סגירת תבנית ה-JSON בצורה תקינה
        for name, f in self.files.items():
            f.write('\n]\n')
            f.close()

# הרצה עם המחלקה החדשה שיצרנו
process = CrawlerProcess(settings={
    'ITEM_PIPELINES': {
        '__main__.JsonWriterPipeline': 1 # קורא למנגנון השמירה שלנו
    },
    'LOG_LEVEL': 'INFO' # יראה לכן פחות טקסט רץ בטרמינל כדי לא להעמיס
})

process.crawl(ScrollsWordSpider)
process.start()