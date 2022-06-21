from cmath import e
import requests
from bs4 import BeautifulSoup
import warnings
import json
import time

class JishoRetriever:
    def __init__(self,*,information=False,block_size=100, pause=0) -> None:
        self.__inf = information
        self.__total = None
        self.__partitioned = False
        self.__block_size = block_size
        self.__pause_between_requests = pause

    def enable_information(self):
        self.__inf = True
    def disable_information(self):
        self.__inf = False

    def generate_info_json_by_level(self, level:int, file_rad="output/kanji_"):
        if self.__inf:
            print(f"Retrieving level N{level} kanji")
        kanji = self.get_kanji_list_by_level(level)

        self.__total = len(kanji)
        total = self.__total

        kanji_blocks = []
        while len(kanji) > self.__block_size:
            kanji_blocks.append(kanji[:self.__block_size])
            kanji = kanji[self.__block_size+1:]
        kanji_blocks.append(kanji)

        self.__partitioned = True
        self.__count = 1
        for i in range(len(kanji_blocks)):
            gen = self.generate_info_json_by_kanji_list(kanji_blocks[i])
            file_name = f"{file_rad}n{level}"
            if len(kanji_blocks) > 1:
                file_name = f"{file_name}_{i+1}"
            
            file = open(file_name,"w", encoding="utf8")
            json.dump(gen, file, indent=4,ensure_ascii=False)
            file.close()
            if self.__inf:
                print(f"file \"{file_name}\" created")

        self.__partitioned = False
        if self.__inf:
            print(f"{total} kanji have been successfully retrieved")


    def get_kanji_list_by_level(self, level:int):
        page = 1
        r = requests.get(f'https://jisho.org/search/%23kanji%20%23jlpt-n{level}?page={page}')
        html = r.content
        parsed_html = BeautifulSoup(html, features="html.parser")

        span_list = parsed_html.find_all('span', attrs={'class':'character literal japanese_gothic'})
        
        output = []
        total = 0
        while len(span_list) != 0:
            for span in span_list:
                output.append(span.find('a').text)
            total += len(span_list)
            
            if self.__inf:
                print(f"page {page} completed - {total} kanji retrieved" )


            page+=1
            r = requests.get(f'https://jisho.org/search/%23kanji%20%23jlpt-n{level}?page={page}')
            html = r.content
            parsed_html = BeautifulSoup(html, features="html.parser")
            span_list = parsed_html.find_all('span', attrs={'class':'character literal japanese_gothic'})

        return output



    def generate_info_json_by_kanji_list(self, kanji_list):
        output = []
        if not self.__partitioned:
            self.__total = len(kanji_list)
            self.__count = 1
        if self.__inf:
            print(f"Retrieving {self.__total} kanji")
        for kanji in kanji_list:
            output.append(self.get_kanji_info(kanji))
            time.sleep(self.__pause_between_requests)
        
        if not self.__partitioned and self.__inf:
            print(f"{self.__total} kanji have been successfully retrieved")
        if not self.__partitioned:
            self.__total = None
        return output
    
    def get_kanji_info(self, kanji):
        r = requests.get(f'https://jisho.org/search/{kanji}%23kanji')
        html = r.content
        parsed_html = BeautifulSoup(html, features="html.parser")


        output = {"kanji":kanji}

        readinghtml = parsed_html.body.find('div', attrs={'class':'kanji-details__main-readings'})

        try:
            kunhtml = readinghtml.find('dl', attrs={'class':'dictionary_entry kun_yomi'})
            kun_a = kunhtml.find_all('a')
            kun_list = []
            for a in kun_a:
                kun_list.append(a.text)
        except:
            kun_list = []
        
        output["kun"] = kun_list
        
        try:
            onhtml = readinghtml.find('dl', attrs={'class':'dictionary_entry on_yomi'})
            on_a = onhtml.find_all('a')
            on_list = []
            for a in on_a:
                on_list.append(a.text)
        except:
            on_list = []

        output["on"] = on_list
        

        strokeshtml = parsed_html.body.find('div', attrs={'class':'kanji-details__stroke_count'})
        output["strokes"] = int(strokeshtml.find('strong').text)

        try:
            radicalhtml, partshtml = parsed_html.body.find_all('div', attrs={'class':'radicals'})[:2]

            output["radical"] = radicalhtml.find('dd').text.strip().replace('\n','').replace(' ', '').replace(',',', ')

            parts_a = partshtml.find_all('a')
            parts_list = []
            for a in parts_a:
                parts_list.append(a.text)
            output["parts"] = parts_list
        except:
            output["radical"] = []
            output["parts"] = []
            warnings.warn("Warning: can't find radical and parts")


        try:
            meaningshtml = parsed_html.body.find('div', attrs={'class':'kanji-details__main-meanings'})
            output["meanings"] = meaningshtml.text.replace(' ', '').replace('\n','').split(',')
        except:
            output["meanings"] = []
            warnings.warn("Warning: can't find meanings")

        try:
            output["jlpt_level"] = parsed_html.body.find('div', attrs={'class':'jlpt'}).find('strong').text
        except:
            output["jlpt_level"] = "Unknown"
            warnings.warn("Warning: can't find jlpt level")


        examples = []
        try:
            compoundshtml = parsed_html.body.find('div', attrs={'class':'row compounds'})
            for li in compoundshtml.find_all('li'):
                p1,p23 = li.text.split('【')
                p2,p3 = p23.split('】')
                p1 = p1.strip()
                p2 = p2.strip()
                p3 = p3.strip()
                examples.append({'word':p1,'reading':p2,'meaning':p3})
        except:
            examples = []

        output['examples'] = examples
        
        if self.__inf:
            if self.__total != None:
                print(f"{self.__count} out of {self.__total} kanji retrieved ({self.__count*100//self.__total}%)")
                self.__count+=1
            else:
                print(f"kanji successfully retrieved")


        return output
