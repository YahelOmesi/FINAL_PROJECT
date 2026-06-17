import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os
import re

# הגדרת המקטעים של ספר חנוך לפי האתר של CAL
ENOCH_CONFIG = {
    '4Q201_4QEn_a': '44403201',
    '4Q202_4QEn_b': '44403202',
    '4Q204_4QEn_c': '44403204',
    '4Q205_4QEn_d': '44403205',
    '4Q206_4QEn_e': '44403206',
    '4Q207_4QEn_f': '44403207',
    '4Q212_4QEn_g': '44403212'
}

def parse_word(response):
    word = response.meta['word']

    # --- התיקון: חילוץ תגיות דקדוק בשיטת המגילות ---
    pos_tags = response.xpath('//pos//text()').getall()
    bin_tags = response.xpath('//span[@class="bin"]//text()').getall()
    all_grammar_tags = [t.strip() for t in pos_tags + bin_tags if t.strip()]
    
    if all_grammar_tags:
        word['lexicon_0'] = " ".join(all_grammar_tags)
    else:
        word['lexicon_0'] = None
        
    # המשך חילוץ לקסיקונים נוספים
    for i in range(1, 5):
        lex = response.xpath(f'//body/hr[{i}]/following-sibling::text()').get()
        if lex and lex.strip() != '':
            word[f'lexicon_{i}'] = lex.strip()
        else:
            word[f'lexicon_{i}'] = None

    # חילוץ המשמעויות (Meanings)
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
        meanings = response.xpath('//span[@class="mgP"]/text()').getall()
        meanings = [m.strip() for m in meanings if m.strip()]
        for i in range(4):
            word[f'meaning_{i}'] = meanings[i] if i < len(meanings) else None

    # חילוץ פיצול מילים (Split Words)
    split_words = response.xpath('//span[@class="lem"]/font/text()').getall()
    split_words = [w.strip() for w in split_words if w.strip()]
    for i in range(4):
        word[f'split_word_{i}'] = split_words[i] if i < len(split_words) else None

    yield word

class EnochSpider(scrapy.Spider):
    name = 'enoch_spider'
    
    def start_requests(self):
        for scroll_name, base_code in ENOCH_CONFIG.items():
            url = f"https://cal.huc.edu/get_a_chapter.php?file={base_code}&cset=H"
            yield scrapy.Request(url=url, meta={'scroll_name': scroll_name}, callback=self.parse)

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

# Pipeline ששומר את כל הקבצים בקובץ JSON אחד מרוכז
class SingleJsonWriterPipeline:
    def open_spider(self, spider):
        self.output_dir = os.path.join('..', 'Data', 'Data_Enoch')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.file_path = os.path.join(self.output_dir, 'Enoch_All.json')
        self.file = open(self.file_path, 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        else:
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
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'DOWNLOAD_DELAY': 0.5,
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(EnochSpider)
    process.start()