import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os

# Configuration for target scrolls (CAL base code and chapter range)
SCROLLS_CONFIG = {
    '1QapGen_Genesis_Apocryphon': {'base_code': '44404', 'range': 23}, 
    '11QtgJob_Job_Scroll': {'base_code': '44001', 'range': 39}         
}

def parse_word(response):
    """Extracts morphological tags and lemmas for a single word."""
    word = response.meta['word']
    
    # Extract and merge POS and binary tags
    pos_tags = response.xpath('//pos//text()').getall()
    bin_tags = response.xpath('//span[@class="bin"]//text()').getall()
    all_grammar_tags = [t.strip() for t in pos_tags + bin_tags if t.strip()]
    
    if all_grammar_tags:
        word['lexicon_0'] = " ".join(all_grammar_tags)
    else:
        word['lexicon_0'] = None
        
    # Initialize placeholders for additional lexicon features
    for i in range(1, 5):
        word[f'lexicon_{i}'] = None

    # Extract up to 4 base word components (lemmas)
    split_words = response.xpath('//span[@class="lem"]//text()').getall()
    split_words = [w.strip() for w in split_words if w.strip()] 
    for i in range(4):
        word[f'split_word_{i}'] = split_words[i] if i < len(split_words) else None

    # Extract up to 4 semantic meanings
    meanings = response.xpath('//span[contains(@class, "mgP") or contains(@class, "mg1")]//text()').getall()
    meanings = [m.strip() for m in meanings if m.strip() and not m.strip().isnumeric()] 
    for i in range(4):
        word[f'meaning_{i}'] = meanings[i] if i < len(meanings) else None
        
    yield word

class ScrollsWordSpider(scrapy.Spider):
    """Spider to crawl scroll chapters and extract word links."""
    name = 'scrolls_spider'
    
    def start_requests(self):
        # Generate initial requests for each chapter based on SCROLLS_CONFIG
        for name, config in SCROLLS_CONFIG.items():
            for i in range(1, config['range']):
                url = f"https://cal.huc.edu/get_a_chapter.php?file={config['base_code']}{i:02d}"
                yield scrapy.Request(url, meta={'scroll_name': name})

    def parse(self, response):
        # Find all word links in the chapter and yield requests to parse them
        scroll_name = response.meta['scroll_name']
        for el in response.css('tr > td:nth-child(2) > a'):
            word = {'text': el.css('::text').get(), 'url': el.xpath('@href').get(), 'scroll_name': scroll_name}
            yield scrapy.Request(url=f"https://cal.huc.edu/{word['url']}", meta={'word': word}, callback=parse_word)

class JsonWriterPipeline:
    """Pipeline to save scraped items into JSON files per scroll."""
    def open_spider(self, spider):
        self.files = {}
        # Define output directory: ../Data/Data_Scrolls
        self.output_dir = os.path.join('..', 'Data', 'Data_Scrolls')
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        name = item['scroll_name']
        
        # Open file and initialize JSON array if it's the first item
        if name not in self.files:
            file_path = os.path.join(self.output_dir, f'{name}.json')
            self.files[name] = open(file_path, 'w', encoding='utf-8')
            self.files[name].write('[\n')
        else:
            self.files[name].write(',\n') # Append comma for subsequent items
        
        line = json.dumps(dict(item), ensure_ascii=False)
        self.files[name].write(line)
        return item

    def close_spider(self, spider):
        # Properly close JSON arrays and files
        for name, f in self.files.items():
            f.write('\n]\n')
            f.close()

# Run the spider with the custom JSON pipeline
process = CrawlerProcess(settings={'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, 'LOG_LEVEL': 'INFO'})
process.crawl(ScrollsWordSpider)
process.start()