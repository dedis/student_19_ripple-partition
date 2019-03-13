import pandas as pd
import numpy as np
from caida_helper import *

def main():
    debug = False
    nodes_file = 'kapar-midar-iff.nodes.txt'
    nodes_as_file = 'kapar-midar-iff.nodes.as.txt'
    nodes_geo_file = 'kapar-midar-iff.nodes.geo.txt'
    links_file = 'kapar-midar-iff.links.txt'
    
    #nodes = get_nodes(nodes_file, debug)
    print('Get nodes')
    nodes_as = get_nodes_as(nodes_as_file, debug)
    print('Get nodes_as')
    #nodes_geo = get_nodes_geo(nodes_geo_file, debug)
    print('Get nodes_geo')
    links = get_links(links_file, debug)
    print('Get links')
    
    #nodes = nodes.join(nodes_as)
    #nodes = nodes.join(nodes_geo)
    print('nodes complete')
    
    links_as = get_links_as(nodes_as,links)
    
    #nodes.to_csv('nodes.csv', sep=',', encoding='ISO-8859-1')
    print('nodes saved')
    #links.to_csv('links.csv', sep=',', encoding='ISO-8859-1')
    print('links saved')
    links_as.to_csv('links_as.csv', sep=',', encoding='ISO-8859-1')
    print('links_nodes saved')
    
    print('Done')
    

if __name__ == "__main__":
    main()