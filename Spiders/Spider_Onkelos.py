import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os
import re

# הגדרת המקטעים של אונקלוס (חמישה חומשי תורה) וכמות הפרקים לכל ספר
# ה-range הוא מספר הפרקים בפועל + 1 (עבור לולאת ה-for)[cite: 2]
ONKELOS_CONFIG = {
    'TgO_Genesis': {'base_code': '51001', 'range': 51},     # בראשית: 50 פרקים
    'TgO_Exodus': {'base_code': '51002', 'range': 41},      # שמות: 40 פרקים
    'TgO_Leviticus': {'base_code': '51003', 'range': 29},   # ויקרא: 27 פרקים
    'TgO_Numbers': {'base_code': '51004', 'range': 37},     # במדבר: 36 פרקים
    'TgO_Deuteronomy': {'base_code': '51005', 'range': 35}  # דברים: 34 פרקים
}

def parse_word(response):
    word = response.meta['word']

    # חילוץ תגיות דקדוק בשיטת המגילות[cite: 1, 2]
    pos_tags = response.xpath('//pos//text()').getall()
    bin_tags = response.xpath('//span[@class="bin"]//text()').getall()
    all_grammar_tags = [t.strip() for t in pos_tags + bin_tags if t.strip()]
    
    if all_grammar_tags:
        word['lexicon_0'] = " ".join(all_grammar_tags)
    else:
        word['lexicon_0'] = None
        
    # חילוץ לקסיקונים נוספים[cite: 1]
    for i in range(1, 5):
        lex = response.xpath(f'//body/hr[{i}]/following-sibling::text()').get()
        if lex and lex.strip() != '':
            word[f'lexicon_{i}'] = lex.strip()
        else:
            word[f'lexicon_{i}'] = None

    # חילוץ המשמעויות (Meanings) בשיטה המשולבת[cite: 1]
    translation_list = response.xpath('//span[@class="mgT"]/text()').getall()
    if translation_list:
        cleaned_translations = []
        for t in translation_list:
            t = t.strip()
            if t and not re.match(r'^\d+$', t):
                cleaned_translations.append(t)
        for i in range(4):
            word[f'meaning_{i}'] = cleaned_translations[i] if i < len(cleaned_translations) else None
    else:
        # גיבוי למקרה שאין mgT, מחפש mgP או mg1[cite: 2]
        meanings = response.xpath('//span[contains(@class, "mgP") or contains(@class, "mg1")]//text()').getall()
        meanings = [m.strip() for m in meanings if m.strip() and not m.strip().isnumeric()]
        for i in range(4):
            word[f'meaning_{i}'] = meanings[i] if i < len(meanings) else None

    # חילוץ פיצול מילים (Split Words)[cite: 1, 2]
    split_words = response.xpath('//span[@class="lem"]//text()').getall()
    split_words = [w.strip() for w in split_words if w.strip()]
    for i in range(4):
        word[f'split_word_{i}'] = split_words[i] if i < len(split_words) else None

    yield word

class OnkelosSpider(scrapy.Spider):
    name = 'onkelos_spider'
    
    def start_requests(self):
        for name, config in ONKELOS_CONFIG.items():
            for i in range(1, config['range']):
                # יצירת ה-URL עם הקידומת ומספר הפרק בפורמט דו-ספרתי (למשל 01)[cite: 2]
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

# Pipeline ששומר את הנתונים לפי ספר בתיקיית Data_Onkelos[cite: 2]
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.files = {}
        self.is_first_item = {} # מעקב אחרי האיבר הראשון לכל קובץ כדי למנוע שגיאות JSON[cite: 1]
        
        # יצירת תיקיית Data_Onkelos
        self.output_dir = os.path.join('..', 'Data', 'Data_Onkelos')
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        name = item['scroll_name']
        if name not in self.files:
            file_path = os.path.join(self.output_dir, f'{name}.json')
            self.files[name] = open(file_path, 'w', encoding='utf-8')
            self.files[name].write('[\n')
            self.is_first_item[name] = True
        else:
            self.files[name].write(',\n')
            
        self.is_first_item[name] = False
        
        line = json.dumps(dict(item), ensure_ascii=False)
        self.files[name].write(line)
        return item

    def close_spider(self, spider):
        for name, f in self.files.items():
            f.write('\n]\n')
            f.close()

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1},
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'DOWNLOAD_DELAY': 0.5, # השהייה כדי לא להעמיס על השרת של CAL[cite: 1]
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(OnkelosSpider)
    process.start()