import pandas as pd 
import numpy as np
import socket
from ipwhois import IPWhois
import requests
import hashlib
import base58

def get_validator_topology():
    url = 'https://data.ripple.com/v2/network/topology?verbose=True'
    result = requests.get(url).json()

    nodes_raw = result['nodes']
    links_raw = result['links']

    nodes = pd.DataFrame.from_dict(nodes_raw)
    links = pd.DataFrame.from_dict(links_raw)

    return nodes, links

def get_gateways_topology():
    links = set()
    with open('gateway_links.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            links.add(tuple(row))
            
    nodes = set ()
    for l in links:
        n1 = l[0]
        n2 = l[1]
        nodes.add(n1)
        nodes.add(n2)
    return nodes, links

def get_gateways_df():
    url = 'https://data.ripple.com/v2/gateways'
    result = requests.get(url).json()

    gateway_dict = {}
    for currency in result:
        for elem in result[currency]:
            name = elem['name']
            account = elem['account']
            domain, curr_set = get_domain(account)
            ip_list = get_ip(domain)
            gateway_dict[account] = {'name' : name, 'domain' : domain, 'currencies': curr_set, 'ip': ip_list}
    
    gateways_df = pd.DataFrame.from_dict(gateway_dict,orient='index')

    gateways_df['asn'], gateways_df['countries'] = zip(*gateways_df['ip'].apply(lambda x: get_as(x)))

    countries = pd.read_csv('country.csv', delimiter=',')
    country_dict = countries.set_index('ISO 3166 Country Code')[['Latitude','Longitude']].dropna().to_dict()

    gateways_df['latitude'] = gateways_df['countries'].apply(lambda x: country_dict['Latitude'].get(x),np.nan)
    gateways_df['longitude'] = gateways_df['countries'].apply(lambda x: country_dict['Longitude'].get(x,np.nan))

    return gateways_df

def key_to_account(test_key):
    default_base58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    ripple_base58 = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'

    default_to_ripple = dict(zip(default_base58, ripple_base58))
    ripple_to_default = dict(zip(ripple_base58, default_base58))
    
    pubkey_inner_hash = hashlib.sha256(test_key)
    pubkey_outer_hash = hashlib.new('ripemd160')
    pubkey_outer_hash.update(pubkey_inner_hash.digest())
    account_id = pubkey_outer_hash.digest()

    address_type_prefix = bytearray(b'\x00')
    payload = address_type_prefix + bytearray(account_id)
    chksum_hash1 = hashlib.sha256(payload).digest()
    chksum_hash2 = hashlib.sha256(chksum_hash1).digest()
    checksum = chksum_hash2[:4]
    
    dataToEncode = payload + checksum
    address = base58.b58encode(bytes(dataToEncode))
    return ''.join([default_to_ripple[letter] for letter in address.decode('utf-8')])

#################################
######## PRIVATE METHODS ########
#################################

def get_as(x):
    if type(x) is float:
        return np.nan, np.nan
    as_list = set()
    gateways_countries = set()
    for ip in x:
        try:
            obj = IPWhois(ip)
            result = obj.lookup_whois()
            as_list.add(result['asn'])
            gateways_countries.add(result['asn_country_code'])
        except:
            print('ERROR with ' + ip)
    return as_list, next(iter(gateways_countries))

def get_ip(domain):
    try:
        return socket.gethostbyname_ex(domain)[2]
    except:
        return np.nan
    
def get_domain(account):
    domain = ''
    
    url = 'https://data.ripple.com/v2/gateways/' + account
    result = requests.get(url).json()
    if 'domain' in result:
        domain =  result['domain']
    else:
        domain = np.nan
        
    if account == 'razqQKzJRdB4UxFPWf5NEpEG3WMkmwgcXA':
        domain = 'wg.iripplechina.com'
    
    if account == 'rcoef87SYMJ58NAFx7fNM5frVknmvHsvJ':
        domain = 'bpgrefining.com'
    
    if account == 'rsP3mgGb2tcYUrxiLFiHJiQXhsziegtwBc':
        domain = 'coinex.co.nz'
    
    curr_set = set()
    if 'accounts' in result:
        for acc in result['accounts']:
            for c in(acc['currencies']):
                curr_set.add(c)
    return domain, curr_set





