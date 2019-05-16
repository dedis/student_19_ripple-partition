import pandas as pd
import numpy as np
import networkx as nx
import csv

## Recover Ripple Graph
def recover_ripple(filename):
    links = set()
    ases = set()
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            l = tuple(row)
            links.add(l)
            ases.add(l[0])
            ases.add(l[1])

    ripple_graph = nx.Graph()
    ripple_graph.add_nodes_from(ases)
    return ripple_graph

## Recover Caida Graph
def recover_caida(filename):
    data = pd.read_csv(filename,delimiter='\n', comment='#', header=None, encoding='ISO-8859-1')

    data['provider_peer'], data['customer_peer'], data['relation_type'], data['source'] = data[0].str.split('|').str
    data['relation_type']  = data['relation_type'].apply(lambda x: 'provider-customer' if x == '-1' else 'peer-peer')
    links = data[['provider_peer','customer_peer','relation_type']]

    caida_ases = set(links['provider_peer'].values)
    caida_ases.update(links['customer_peer'].values)

    links['link'] = list(zip(links['provider_peer'], links['customer_peer']))
    links = links[['link','relation_type']]
    caida_links = {}
    for index,row in links.iterrows():
        (s,t) = row['link']
        rel = row['relation_type']
        if rel == 'provider-customer':
            caida_links[tuple([s,t])] = rel
            caida_links[tuple([t,s])] = 'customer-provider'
        else: 
            if rel == 'peer-peer':
                caida_links[tuple([s,t])] = rel
                caida_links[tuple([t,s])] = 'peer-peer'
            else:
                print('Error')

    caida_graph = nx.Graph()
    caida_graph.add_nodes_from(caida_ases)
    for k,v in caida_links.items():
        caida_graph.add_edge(k[0],k[1],relation=v)

    return caida_graph, caida_links

## Add intermediary nodes to ripple
def build_ripple_from_caida(ripple_graph, caida_graph):
    ripple_ases = list(ripple_graph.nodes).copy()
    for s in ripple_ases:
        for t in ripple_ases:
            paths = nx.all_shortest_paths(caida_graph,s,t)
            for p in paths:
                complete_path = [s] + p
                for i in range(len(complete_path)-1):
                    n1 = complete_path[i]
                    n2 = complete_path[i+1]
                    if(n1 != n2):
                        rel = caida_graph.get_edge_data(n1,n2)['relation']
                        ripple_graph.add_edge(complete_path[i],complete_path[i+1], relation=rel)
    return ripple_graph

def build_graphs(filename_ripple, filename_caida):
    ripple_graph = recover_ripple(filename_ripple)
    caida_graph, caida_links = recover_caida(filename_caida)
    ripple_graph_final = build_ripple_from_caida(ripple_graph, caida_graph)
    return ripple_graph_final, caida_graph, list(ripple_graph.nodes)
                                                
## Retrieve transactions
def get_transactions(filename):
    transactions = pd.read_csv(filename, dtype={'sender': str, 'receiver': str, 'amount': np.float64} )
    transactions = transactions[['sender','receiver','amount','date']]
    return transactions

## tie_breaker

def rel_type(rel):
    if (rel == 'customer-provider'):
        return 2
    if (rel == 'peer-peer'):
        return 1
    if (rel == 'provider-customer'):
        return 0
    return None

def compare_rel(paths, index, ripple_graph):
    best_p = []
    best_rel = 3
    for p in paths:
        start = p[index]
        end = p[index+1]
        rel = rel_type(ripple_graph.get_edge_data(start,end)['relation'])
        if (rel < best_rel):
            best_p = [p]
            best_rel = rel
        elif (rel == best_rel):
            best_p.append(p)
    return best_p

def select_best(source, dest, ripple_graph):
    paths = list(nx.all_shortest_paths(ripple_graph,source,dest))
    ## If only one path, return it
    if(type(paths[0]) == str):
        return paths
    
    ## Assume all paths have same length
    l = len(paths[0])
    temp_paths = paths
    for i in range(0,l-1):
        temp_paths = compare_rel(temp_paths, i, ripple_graph)
    
    if (len(temp_paths) >= 1):
        return temp_paths[0]
    return temp_paths

## Analysis
def compute_best_paths(ripple_graph):
    best_paths = {}
    for source in ripple_graph.nodes:
        for dest in ripple_graph.nodes:
            if(source != dest):
                path = select_best(source,dest,ripple_graph)
                best_paths[(source,dest)] = path
    return best_paths

def replay_transactions_remove(transactions, corrupted_graph, complete_graph, best_paths):
    amount_ok = 0
    amount_lost = 0
    amount_rerouted = 0
        
    for index, row in transactions.iterrows():
        sender = row['sender']
        receiver = row['receiver']
        try :
            amount = row['amount']
            path_corrupted = select_best(sender,receiver,corrupted_graph)
            
            #path_ok = select_best(list(nx.all_shortest_paths(complete_graph,sender,receiver)))
            path_ok = best_paths[(sender,receiver)]
            if (path_corrupted == path_ok):
                amount_ok += amount
            else:
                amount_rerouted += amount
        except:
            #print('No path between {} and {}'.format(sender,receiver))
            amount_lost += amount
    return amount_ok, amount_lost, amount_rerouted

def generate_remove_analysis(ripple_graph, transactions, gateways, best_paths):
    df_corrupted = pd.DataFrame(columns=['corrupted', 'amount_ok', 'amount_lost', 'amount_rerouted'])
    intermediaries = set()
    for source in gateways:
        for dest in gateways:
            if(source != dest):
                path = best_paths[(source,dest)]
                intermediaries.update(path)
         
    for c in intermediaries:
        corrupted_graph = ripple_graph.copy()
        corrupted_graph.remove_node(c)
        amount_ok, amount_lost, amount_rerouted = replay_transactions_remove(transactions, corrupted_graph, ripple_graph, best_paths)
        df_corrupted = df_corrupted.append({'corrupted': c, 'amount_ok': amount_ok, 'amount_lost': amount_lost, 'amount_rerouted': amount_rerouted}, ignore_index=True)

    return df_corrupted


def replay_transactions_hijack(transactions, corrupted_node, complete_graph, best_paths):
    amount_ok = 0
    amount_lost = 0
    amount_rerouted = 0
    for index, row in transactions.iterrows():
        sender = row['sender']
        receiver = row['receiver']
        
        if(corrupted_node != sender and corrupted_node != receiver):
            try :
                amount = row['amount']
                #path_ok = select_best(list(nx.all_shortest_paths(complete_graph,sender,receiver)))
                path_ok = best_paths[(sender,receiver)]

                #path_to_corrupted = select_best(list(nx.all_shortest_paths(complete_graph, sender, corrupted_node)))
                #path_from_corrupted = select_best(list(nx.all_shortest_paths(complete_graph, corrupted_node, receiver)))
                path_corrupted = best_paths[(sender, corrupted_node)]
                
                if (len(path_corrupted) + 1 > len(path_ok)):
                    amount_ok += amount
                else:
                    amount_rerouted += amount
            except:
                #print('No path between {} and {}'.format(sender,receiver))
                amount_lost += amount
    return amount_ok, amount_lost, amount_rerouted

def generate_hijack_analysis(ripple_graph, transactions, best_paths):
    df_corrupted = pd.DataFrame(columns=['corrupted', 'amount_ok', 'amount_lost', 'amount_rerouted'])
    for c in ripple_graph.nodes:
        amount_ok, amount_lost, amount_rerouted = replay_transactions_hijack(transactions, c, ripple_graph, best_paths)
        df_corrupted = df_corrupted.append({'corrupted': c, 'amount_ok': amount_ok, 'amount_lost': amount_lost, 'amount_rerouted': amount_rerouted}, ignore_index=True)

    return df_corrupted