import twitter
import json
import time
import pandas as pd
import re

def transpose(array):
    transposed = zip(*array)
    return transposed

def spread(arg):
    ret = []
    for i in arg:
        if isinstance(i, list):
            ret.extend(i)
        else:
            ret.append(i)
    return ret

def deep_flatten(xs):
    flat_list = []
    [flat_list.extend(deep_flatten(x)) for x in xs] if isinstance(xs, list) else flat_list.append(xs)
    return flat_list

def to_dictionary(keys, values):
    return dict(zip(keys, values))

def merge_dicts(a, b):
    #return {**a, **b} # python 3.5+
    c = a.copy()   # make a copy of a 
    c.update(b)    # modify keys and values of a with the ones from b
    return c

def min_type(x):
    for typ in [int,float,str]:
        try:
            return x.astype(typ, casting='safe')
        except:
            pass
    return x

def text_clean(x,lower=True,url=False,emoji=False,slash=False,rep=False):
    if lower:
        x = str(x).lower() # all lower case
    if not url:
        x = re.sub(r'https?://\w+\.\w+((\/\S+)+)?',r'',x) # remove URLS
    if not emoji:
        x = re.sub(r'\\x[a-z0-9]{2}',r'',x) # remove emojis
    if not slash:
        x = re.sub(r'[\\\_\/]',r'',x) # remove slashes and underscores
    if not rep: 
        x = re.sub(r'([a-z])\1{3,}', r'\1\1', x) # remove >3x repeated characters i.e. loooooook -> look
    
    return x