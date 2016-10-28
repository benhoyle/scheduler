# -*- coding: utf-8 -*-

# Generic helper functions

import datetime
import re

# Common useful utilities

def check_list(listvar):
    """Turns single items into a list of 1."""
    if not isinstance(listvar, list):
        listvar = [listvar]
    return listvar

def safeget(dct, *keys):
    """ Recursive function to safely access nested dicts or return None. 
    param dict dct: dictionary to process
    param string keys: one or more keys"""
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def keysearch(d, key):
    """Recursive function to look for first occurence of key in multi-level dict. 
    param dict d: dictionary to process
    param string key: key to locate"""
 
    if isinstance(d, dict):
        if key in d:
            return d[key]
        else:
            if isinstance(d, dict):
                for k in d:
                    found = keysearch(d[k], key)
                    if found:
                        return found
            else:
                if isinstance(d, list):
                    for i in d:
                        found = keysearch(d[k], key)
                        if found:
                            return found

# Define helper function to remove text in parenthesis
# From http://stackoverflow.com/questions/14596884/remove-text-between-and-in-python
def remove_bracketed(test_str):
    """ Remove bracketed text from string. """
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in test_str:
        if i == '[':
            skip1c += 1
        elif i == '(':
            skip2c += 1
        elif i == ']' and skip1c > 0:
            skip1c -= 1
        elif i == ')'and skip2c > 0:
            skip2c -= 1
        elif skip1c == 0 and skip2c == 0:
            ret += i
    return ret
    
# Get current year and look for publications in that year
def get_current_year():
    """ Get current year. """
    now = datetime.datetime.now()
    return now.year
    
def list_frequencies(list_of_items):
    """ Determine frequency of items in list_of_items. """
    itemfreq = [list_of_items.count(p) for p in list_of_items] 
    return dict(zip(list_of_items,itemfreq))

def sort_freq_dist(freqdict): 
    """ Sort frequency distribution. """
    aux = [(freqdict[key], key) for key in freqdict]
    aux.sort() 
    aux.reverse() 
    return aux

def hasNumbers(inputString):
    """ Return true if inputString contains numbers. """
    return any(char.isdigit() for char in inputString)

def hasReNumbers(inputString):
    """ Return true if inputString contains numbers. Using regex."""
    return bool(re.search(r'\d', inputString))