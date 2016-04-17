import os
import codecs
import re
import logging

_logger = logging.getLogger(__name__)

def _year_from_filepath(filepath):
    match = re.match(
        r'^[a-zA-Z]*([0-9]{4}).txt', 
        os.path.basename(filepath))
    if match:
        return int(match.group(1))
    else:
        _logger.warning('failed to get year from file "{0}"'.format(filepath))
    return -1

def _load_file(name_filepath):
    year = _year_from_filepath(name_filepath)
    name_file = codecs.open(name_filepath)
    names = []
    for line in name_file:
        tokens = line.strip().split(',')
        if len(tokens) != 3:
            _logger.warning('could not parse line "{0}"'.format(line))
            continue
        name = tokens[0]
        entry = {
            'name': name,
            'year': year,
            'gender': tokens[1],
            'count': int(tokens[2])
        }
        names.append(entry)
    return names

def _load_directory(name_directory):
    filenames = os.listdir(name_directory)
    filenames = filter(lambda x: os.path.splitext(x)[1].lower() == '.txt', filenames)
    filepaths = map(lambda x: os.path.join(name_directory, x), filenames)

    names = []
    for filepath in filepaths:
        _logger.debug('loading file "{0}"'.format(filepath))
        year_names = _load_file(filepath)
        names.extend(year_names)
    return names

def load(name_directory):
    '''
    Loads US social security data from "name_directory" 
    Returns a dictionary of names
    '''
    names = _load_directory(name_directory)
    return names

