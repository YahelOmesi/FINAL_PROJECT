import scrapy 
from scrapy.crawler import CrawlerProcess
import json
import os
import re

# Configuration for the five books of the Torah in Targum Onkelos.
# The `range` value is exclusive and is therefore set to the number of chapters plus one.
ONKELOS_CONFIG = {
    'TgO_Genesis': {'base_code': '51001', 'range': 51},     # Genesis: 50 chapters
    'TgO_Exodus': {'base_code': '51002', 'range': 41},      # Exodus: 40 chapters
    'TgO_Leviticus': {'base_code': '51003', 'range': 28},   # Leviticus: 27 chapters
    'TgO_Numbers': {'base_code': '51004', 'range': 37},     # Numbers: 36 chapters
    'TgO_Deuteronomy': {'base_code': '51005', 'range': 35}  # Deuteronomy: 34 chapters
}

def parse_word(response):
    word = response.meta['word']

    # Extract grammatical tags from the POS and binary-tag elements.
    pos_tags = response.xpath('//pos//text()').getall()
    bin_tags = response.xpath('//span[@class="bin"]//text()').getall()
    all_grammar_tags = [t.strip() for t in pos_tags + bin_tags if t.strip()]
    
    if all_grammar_tags:
        word['lexicon_0'] = " ".join(all_grammar_tags)
    else:
        word['lexicon_0'] = None
        
    # Extract additional lexicon entries located after the horizontal separators.
    for i in range(1, 5):
        lex = response.xpath(f'//body/hr[{i}]/following-sibling::text()').get()
        if lex and lex.strip() != '':
            word[f'lexicon_{i}'] = lex.strip()
        else:
            word[f'lexicon_{i}'] = None

    # Extract available English meanings from the primary meaning elements.
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
        # Fall back to alternative meaning elements when no primary meanings are available.
        meanings = response.xpath('//span[contains(@class, "mgP") or contains(@class, "mg1")]//text()').getall()
        meanings = [m.strip() for m in meanings if m.strip() and not m.strip().isnumeric()]
        for i in range(4):
            word[f'meaning_{i}'] = meanings[i] if i < len(meanings) else None

    # Extract the individual components of words that are divided into multiple lemmas.
    split_words = response.xpath('//span[@class="lem"]//text()').getall()
    split_words = [w.strip() for w in split_words if w.strip()]
    for i in range(4):
        word[f'split_word_{i}'] = split_words[i] if i < len(split_words) else None

    yield word

# Spider responsible for collecting word-level data from the CAL Onkelos texts.
class OnkelosSpider(scrapy.Spider):
    name = 'onkelos_spider'
    
    def start_requests(self):
        for name, config in ONKELOS_CONFIG.items():
            for i in range(1, config['range']):
                # Build the chapter URL using the book code and a two-digit chapter number.
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

# Pipeline that stores the collected data in a separate JSON file for each book.
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.files = {}
        self.is_first_item = {} # Track the first item written to each output file.
        
        # Create the output directory if it does not already exist.
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
        'DOWNLOAD_DELAY': 0.5, # Add a short delay to avoid overloading the CAL server.
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(OnkelosSpider)
    process.start()