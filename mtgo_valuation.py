## MTGO Valuation
import math, os
from bs4 import BeautifulSoup
from functools import reduce
import xml.etree.ElementTree as xml_tree

def get_prices(src, collection):
    html_cards = BeautifulSoup(open(src), 'html5lib').find_all('dt', {'class': 'priceList-prices-card'})
    html_prices = BeautifulSoup(open(src), 'html5lib').find_all('div', {'class': 'priceList-price-price-wrapper'})
    cards = list(map(lambda x: html_cards[x].text, filter(lambda x: html_prices[x].text.strip() != '-', range(len(list(html_cards))))))
    prices = list(map(lambda x: float(x.text.strip()), filter(lambda x: x.text.strip() != '-', html_prices)))
    if len(cards) != len(prices):
        print('ERROR: Found %d cards and %d prices.' % (len(cards), len(prices)))
    for i in range(len(cards)):
        card = cards[i]
        price = prices[i]
        if card not in collection:
            collection[card] = {'low': price, 'high': price}
        else:
            collection[card]['low'] = min(collection[card]['low'], price)
            collection[card]['high'] = max(collection[card]['high'], price)

def get_all_prices():
    all_prices = {}
    for _file in os.listdir('web/'):
        get_prices('web/%s' % _file, all_prices)
    return all_prices

def get_collection(src):
    xml_root = xml_tree.parse(src).getroot()
    cards = xml_root.getchildren()[2:]
    collection = {}
    for card in cards:
        name = card.get('Name')
        amount = card.get('Quantity')
        _id = carg.get('CatID')
        if name not in collection:
            collection[name] = 0
        collection[name] += int(amount)
    return collection

def valuate(collection, prices):
    valuable_collection = {}
    for card in collection:
        if card in prices:
            valuable_collection[card] = {
                'amount': collection[card],
                'low': prices[card]['low'],
                'high': prices[card]['high']
            }
    return valuable_collection

CONSOLE_FORMAT = '%s x%d: %.2f tix - %.2f tix'
TEXT_FORMAT = '%s%s%d\t%.2f\t%.2f\n'
EXCEL_FORMAT = '%s\t%d\t%.2f\t%.2f\n'
TAB_SIZE = 4
def determine_tabs(tabs, s):
    return tabs - math.floor(len(s) / TAB_SIZE)

def display_valuation(collection, to_console=True, to_file=None):
    max_name_len = reduce(lambda x,y : max(len(y), x), collection, 0)
    tabs = math.ceil(max_name_len / TAB_SIZE) + 1

    if to_file:
        _file = open(to_file, 'w')
        _file.write('Name%sQty\tLow\t\tHigh\n' % ('\t' * determine_tabs(tabs, 'Name')))
        
    for card in collection:
        if to_console:
            print(CONSOLE_FORMAT % (
                card, collection[card]['amount'],
                collection[card]['low'], collection[card]['high']))
        if to_file:
            card_tabs = '\t' * determine_tabs(tabs, card)
            _file.write(TEXT_FORMAT % (
                card, card_tabs, collection[card]['amount'],
                collection[card]['low'], collection[card]['high']))

def main():
    print('Fetching all prices.')
    prices = get_all_prices()
    print('Retrieving collection.')
    collection = get_collection('Magic Online Collection 4-15-2020.dek')
    print('Valuating collection.')
    values = valuate(collection, prices)
    print()
    display_valuation(values, to_file='valuation.txt')

if __name__ == '__main__':
    main()
