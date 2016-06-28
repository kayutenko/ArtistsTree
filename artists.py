# encoding: utf-8
from collections import defaultdict
from string import punctuation
from lxml import etree
from datetime import datetime
from pprint import pprint as pp
from pymystem3.mystem import Mystem
import pandas
from itertools import permutations
import json
import matplotlib.pyplot as plt

class ArtistsExtractor:
    def __init__(self, wiki_dump_file, artist_names):
        self.wiki_dump_file = wiki_dump_file
        self.artist_names = artist_names
        self.mystem = Mystem()
        self.co_occurrences_counts = defaultdict(lambda: defaultdict(int))

    def tokenize_lemmatize(self, text):
        """Returns a list of lemmatized tokens (words of len > 2 only) made from a given string of text"""
        tokenized = [word.lower().strip(punctuation) for word in text.split() if word.isalpha() and len(word) > 2]  # Not the best way, I know
        lemmatized = [lemma for lemma in self.mystem.lemmatize(' '.join(tokenized)) if not lemma == ' ']
        return lemmatized[:-1]

    def texts(self):
        """
        Given a Wikipedia dump filename creates a generator which yields cleaned, tokenized and lemmatized texts
        from elements with <text> tags.
        :return: returns generator object
        """
        for _, element in etree.iterparse(self.wiki_dump_file):
            if 'text' in element.tag and type(element.text) == str:
                yield self.tokenize_lemmatize(element.text)
                element.clear()
            else:
                element.clear()

    def find_artists(self, lemmatized_text):
        """
        Given a list of words representing a tokenized and lemmatized version of a wikipedia page and list of artists
        second names finds all artists that occur in the text and returns them in a set.
        """
        artists_found = set()
        for word in lemmatized_text:
            if word in self.artist_names:
                artists_found.add(word)
        return artists_found

    def count_co_occurrences(self, output):
        last_artists = None
        try:
            for i, text in enumerate(self.texts()):
                if i % 1000 == 0:
                    print(i, 'texts parsed')
                    if last_artists:
                        print('last artists:', last_artists)
                try:
                    artists = self.find_artists(text)
                    if len(artists) > 1:
                        last_artists = artists
                        pairs = set(permutations(artists, 2))
                        for artist1, artist2 in pairs:
                            self.co_occurrences_counts[artist1][artist2] += 1
                except Exception as e:
                    print('Error occurred', e)
                    continue
        except:
            print('Something bad occured...')
            with open('counts_backup.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.co_occurrences_counts, ensure_ascii=False))
        with open(output, 'w', encoding='utf-8') as out:
            out.write(json.dumps(self.co_occurrences_counts, ensure_ascii=False))

class EnglishExtractor(ArtistsExtractor):
    def __init__(self, wiki_dump_files, artist_names, translation_dict):
        super().__init__(wiki_dump_files, artist_names)
        self.translation_dict = translation_dict

    def texts(self):
        for dump in self.wiki_dump_file:
            for _, element in etree.iterparse(dump):
                if 'text' in element.tag and type(element.text) == str:
                    yield self.tokenize_lemmatize(element.text)
                    element.clear()
                else:
                    element.clear()

    def tokenize_lemmatize(self, text):
        tokenized = [word.lower().strip(punctuation) for word in text.split() if
                     word.isalpha() and len(word) > 2]  # Not the best way, I know
        return tokenized

    def count_co_occurrences(self, output):
        last_artists = None
        try:
            for i, text in enumerate(self.texts()):
                if i % 1000 == 0:
                    print(i, 'texts parsed')
                    if last_artists:
                        print('last artists:', last_artists)
                try:
                    artists = self.find_artists(text)
                    if len(artists) > 1:
                        last_artists = artists
                        pairs = set(permutations(artists, 2))
                        for artist1, artist2 in pairs:
                            ru_artist1 = self.translation_dict[artist1]
                            ru_artist2 = self.translation_dict[artist2]
                            self.co_occurrences_counts[ru_artist1][ru_artist2] += 1
                except Exception as e:
                    print('Error occurred', e)
                    continue
        except:
            print('Something bad occured...')
            with open('counts_backup.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.co_occurrences_counts, ensure_ascii=False))
        with open(output, 'w', encoding='utf-8') as out:
            out.write(json.dumps(self.co_occurrences_counts, ensure_ascii=False))

if __name__ == '__main__':
    painters_df = pandas.read_table('painters.tsv')
    russian_names = [painter.split(', ')[0].lower() for painter in list(painters_df['rulabel'])]
    english_names = [painter.split()[-1].lower() for painter in list(painters_df['enlabel'])]
    translation_dict = {}
    for russian, english in zip(russian_names, english_names):
        translation_dict[english] = russian
    # pp(translation_dict)    
    files = ['/media/dmitri/Data/wiki_dump/current4.xml',
             '/media/dmitri/Data/wiki_dump/current5.xml',
             '/media/dmitri/Data/wiki_dump/current6.xml',
             '/media/dmitri/Data/wiki_dump/current7.xml',
             '/media/dmitri/Data/wiki_dump/current8.xml',
             '/media/dmitri/Data/wiki_dump/current1.xml',
             '/media/dmitri/Data/wiki_dump/current2.xml',
             '/media/dmitri/Data/wiki_dump/current3.xml']
    test = EnglishExtractor(files, english_names, translation_dict)
    test.count_co_occurrences('english_counts.json')













