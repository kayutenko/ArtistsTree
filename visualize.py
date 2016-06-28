import json
import networkx as nx
from networkx.readwrite import json_graph
import http_server
from pprint import pprint as pp
import matplotlib.pyplot as plt
import pandas


class Visualiser:
    def __init__(self, artists_counts_file):
        with open(artists_counts_file, 'r', encoding='utf-8') as f:
            self.artists_counts = json.loads(f.read())
        # pp(self.artists_counts)
        self.graph = nx.Graph()

    def make_json(self, painters_to_keep, output):
        seen = set()
        edges = []
        i = 0
        for artist, others in self.artists_counts.items():
            # if i == 10:
            #     break
            overall = sum(others.values())
            for other, count in others.items():
                if artist in painters_to_keep and other in painters_to_keep:
                    if not (other, artist) in seen:
                        edges.append((artist, other, count / overall))
                        seen.add((artist, other))
            i += 1
        final_json= []
        for link in edges:
            final_json.append(dict(source=link[0], target=link[1], weight=link[2]))
        with open(output, 'w', encoding='utf-8') as f:
            f.write('var all_links=' + json.dumps(final_json, ensure_ascii=False) + ';\n')
            f.write('painters = ' + json.dumps(list(painters_to_keep), ensure_ascii=False))


    def draw(self):
        for n in self.graph:
            self.graph.node[n]['name'] = n
        # write json formatted data
        d = json_graph.node_link_data(self.graph)  # node-link format to serialize
        # write json
        json.dump(d, open('force/force.json', 'w'))
        print('Wrote node-link JSON data to force/force.json')
        # open URL in running web browser
        http_server.load_url('force/force.html')
        print('Or copy all files in force/ to webserver and load force/force.html')


if __name__ == '__main__':
    painters_df = pandas.read_table('painters.tsv')
    russian_names = [painter.split(', ')[0].lower() for painter in list(painters_df['rulabel'])]
    test = Visualiser('russian_counts.json')
    test.make_json(set(russian_names[:100]), 'links.json')
    # test.draw()
