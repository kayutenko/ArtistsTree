import json
from pprint import pprint as pp
import matplotlib.pyplot as plt
import pandas


class Visualiser:
    def __init__(self, artists_counts_file):
        with open(artists_counts_file, 'r', encoding='utf-8') as f:
            self.artists_counts = json.loads(f.read())

    def make_json(self, painters_to_keep, output):
        """
        Creates links and nodes along witha list of all artists and writes them in a js object.
        :param painters_to_keep: a list of painters to keep.
        :param output: path to output js object file.
        :return:
        """
        seen = set()
        edges = []
        for artist, others in self.artists_counts.items():
            overall = sum(others.values())
            for other, count in others.items():
                if artist in painters_to_keep and other in painters_to_keep:
                    if not (other, artist) in seen and not (artist, other) in seen:
                        edges.append((artist, other, count / overall))
                        seen.add((artist, other))
        final_json= []
        for link in edges:
            final_json.append(dict(source=link[0], target=link[1], weight=link[2]))
        with open(output, 'w', encoding='utf-8') as f:
            f.write('var all_links=' + json.dumps(final_json, ensure_ascii=False) + ';\n')
            f.write('painters = ' + json.dumps(list(painters_to_keep), ensure_ascii=False))

if __name__ == '__main__':
    painters_df = pandas.read_table('painters.tsv')
    russian_names = [painter.split(', ')[0].lower() for painter in list(painters_df['rulabel'])]
    test = Visualiser('english_counts.json')
    test.make_json(set(russian_names[:100]), 'english_links.json')
    test = Visualiser('russian_counts.json')
    test.make_json(set(russian_names[:100]), 'links.json')