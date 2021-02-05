from typing import Any, Union
import re
from dateutil.parser import parse
from datetime import datetime

def dict_to_opt(dict_:dict, prefix:str='', blacklist:list[str] = []) -> str:
    """convert 'key:value' dict to 'key=value, ...' string

    if there is space in the value, it will automcatically add double quotes around it

    Args:
        dict_ (dict): dict to convert
        prefix (str): prefix put in the front of key
        blacklist (list, optional): if key in the blacklist, it won't convert it
    Returns:
        str: converted string
    """
    assert type(dict_) == dict, 'dict_ should be dict type'
    assert type(prefix) == str, 'prefix should be str type'
    assert type(blacklist) == list, 'blacklist should be list type'

    ret = ''
    for key in dict_.keys():
        
        if key in blacklist:
            continue
        
        
        if type(dict_[key]) == str and ' ' in dict_[key]:
            # if value is str type and there is space in the it, add double quotes around it
            opt = '%s%s "%s"' % (prefix, key, dict_[key])
        else:
            # else, let it be
            opt = '%s%s %s' % (prefix, key, dict_[key])
    
        # append to ret
        ret = ret + ' ' + opt
    
    return ret.strip() # strip space in the head and tail

def read_list(file_path:str) -> list:
    """read str list from txt file

    Args:
        file_path (str): api file path

    Returns:
        list: sorted list without duplicated str
    """
    assert type(file_path) == str, 'file_path should be str type'

    ret =  [ ]

    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line != '':
                ret.append(line)

    ret = list(set(ret))
    ret.sort()
    
    return ret

def value(data:Union[str, None], max_value:int=None) -> Union[str, int, float, datetime, bool, None]:
    """convert value in str to other type as possible
    
    for exmaple:
        turn '' to None
        turn '1.0' to 1.0 of float type
        turn '1' to 1 of int type
        turn '0xFF' to 255 of int type
        turn '1920-10-1 10:11:11' to datetime type
        turn 'true' to True, 'false' to False

    Args:
        data (str or None): the str value to convert, if None, don't convert, just return
        max_value (int, optional): if max_value is not None, when convert int value , and int value is equals to max_value, will return 'null'

    Returns:
        any: converted value
    """
    if data == None:
        return data
    else:
        assert type(data) == str, 'data should be str type'
    
    if max_value != None:
        assert type(max_value) == int, 'max_value should be int type'

    data = data.strip()

    if data == '':
        return None
    
    int_exp = re.compile('^-?(0x|0X)?\d+$')
    float_exp = re.compile('^-?\d+.\d+$')
    bool_true_exp = re.compile('^[Tt][Rr][Uu][Ee]$')
    bool_false_exp = re.compile('^[Ff][Aa][Ll][Ss][Ee]$')
    datetime_exp = re.compile("^\d{4,4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}$")

    if int_exp.match(data):

        intValue = int(data, 10 if data.find('0x') == -1 and  data.find('0x') == -1 else 16)
        if max_value != None and intValue == max_value:

            return 'null'
        else:
            return intValue

    elif float_exp.match(data):

        return float(data)
    
    elif bool_true_exp.match(data):

        return True
        
    elif bool_false_exp.match(data):

        return False

    elif datetime_exp.match(data):

        if data != '0000-00-00 00:00:00':
            
            return parse(data)
        else:
            return None
    else:

        return data

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def remove_empty_lines(lines:str) -> str:
    """remove empty lines

    Args:
        lines (str): lines to deal with

    Returns:
        str: lines without empty line
    """
    assert type(lines) == str, 'lines should be str type'

    ret = [ ]

    lines = lines.splitlines()
    if len(lines) == 1:
        return lines[0]
    else:
        for line in lines:
            if line.strip() != '':
                ret.append(line)
        
        return '\r\n'.join(ret)

__all__ = [
    
    'dict_to_opt',
    'read_list',
    'value',
    'dotdict',
    'remove_empty_lines'
]