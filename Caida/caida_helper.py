import pandas as pd 


def get_nodes(filename):
    data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, names=['nodes'])

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