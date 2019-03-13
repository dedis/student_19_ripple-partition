import pandas as pd 
import numpy as np

def get_nodes(filename, debug):
    # Load data with format (node INDEX: IP INTERFACES)
    if debug:
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'], encoding='ISO-8859-1', nrows=1000)
    else: 
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'], encoding='ISO-8859-1')

    # INDEX: IP INTERFACES
    data['nodes'] = data.nodes.str[5:]

    # INDEX | IP INTERFACES
    data['index'], data['ip'] = data.nodes.str.split(':').str

    # Convert IP interfaces from string to list
    data['ip'] = data['ip'].str[2:-1]
    data['ip'] = data['ip'].str.split(' ')

    nodes = data[['index', 'ip']]
    nodes = nodes.set_index('index')

    return nodes

# Remove IP address for nodes where interface is specified
def keep_nodes(x):
    nodes_list = []
    for n in x:
        nodes_list.append(n.split(':')[0])
    return nodes_list

def get_links(filename, debug):
    # Load data with format (link INDEX: IP INTERFACES)
    if debug:
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['links'], encoding='ISO-8859-1', nrows=1000)
    else:
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['links'], encoding='ISO-8859-1')

    # INDEX: IP INTERFACES
    data['links'] = data.links.str[5:]

    # INDEX | IP INTERFACES
    data['index'], data['links'] = data['links'].str.split(':',1).str
    data['links'] = data['links'].str[2:-1]

    # INDEX: [IP INTERFACES]
    data['links'] = data['links'].str.split(' ')
    data['links'] = data['links'].apply(lambda x: keep_nodes(x))

    links = data[['index', 'links']]
    links = data.set_index('index')
    
    return links

def get_nodes_as(filename, debug):
    # Load data with format (node.AS INDEX AS TYPE)
    if debug:
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'], encoding='ISO-8859-1', nrows=1000)
    else: 
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'], encoding='ISO-8859-1')

    # INDEX AS TYPE
    data['nodes'] = data.nodes.apply(lambda x: x[8:])

    # INDEX | AS
    data['node_index'], data['AS_number'] = data.nodes.str.split(' ').str

    nodes_as = data[['node_index','AS_number']]
    nodes_as = nodes_as.set_index(['node_index'])
    
    return nodes_as

def get_nodes_geo(filename, debug):
    # Load data with format (node.geo INDEX: COUNTRY LATITUDE LONGITUDE)
    if debug:
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'], encoding='ISO-8859-1', nrows=1000)
    else: 
        data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'], encoding='ISO-8859-1')

    # INDEX: COUNTRY LATITUDE LONGITUDE
    data['nodes'] = data.nodes.str[9:-1]

    # INDEX: | COUNTRY | LATITUDE | LONGITUDE
    data['node_index'], data['continent'], data['country'], data['region'], data['city'], data['latitude'],data['longitude'],_,_,_ = data.nodes.str.split('\t').str

    # INDEX | COUNTRY | LATITUDE | LONGITUDE
    data['node_index'] = data['node_index'].str[:-1]

    geo = data[['node_index','country','latitude','longitude']]
    geo = geo.set_index('node_index')
    
    return geo


def apply_list(x, dict_nodes_to_as):
    as_set = set()
    for elem in x:
        as_set.add(dict_nodes_to_as.get(elem, np.nan))
    return as_set

def get_links_as(nodes_as, links):
    dict_nodes_to_as = nodes_as.to_dict()['AS_number']

    links_nodes = links.copy()
    links_nodes['links'] = links_nodes['links'].apply(lambda x: apply_list(x, dict_nodes_to_as))

    return links_nodes 