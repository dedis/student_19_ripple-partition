import pandas as pd 
import requests

def get_topology():
    url = 'https://data.ripple.com/v2/network/topology?verbose=True'
    result = requests.get(url).json()

    nodes_raw = result['nodes']
    links_raw = result['links']

    nodes = pd.DataFrame.from_dict(nodes_raw)
    links = pd.DataFrame.from_dict(links_raw)

    return nodes, links

