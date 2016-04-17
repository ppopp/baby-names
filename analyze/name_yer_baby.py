import os
import sys
import logging
import argparse
import codecs
import re
import operator
import cPickle as pickle
from matplotlib import pyplot

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

def _group_by(field, entries):
    groups = {}
    for entry in entries:
        group = entry[field]
        if not (group in groups):
            groups[group] = []
        groups[group].append(entry)
    return groups

def _merge_genders(names):
    merged = {}
    for name in names:
        key = (name['year'], name['name'])
        if not (key in merged):
            merged[key] = name
            if name['gender'] == 'M':
                merged[key]['male'] = 1.0
            elif name['gender'] == 'F':
                merged[key]['female'] = 1.0
            else:
                _logger.error('failed to parse gender {0}'.format(name))
            merged[key]['gender'] = 'A'

        else:
            total = merged[key]['count'] + name['count']
            if name['gender'] == 'M':
                merged[key]['male'] = float(name['count']) / float(total)
                merged[key]['female'] = float(merged[key]['count']) / float(total)
            elif name['gender'] == 'F':
                merged[key]['female'] = float(name['count']) / float(total)
                merged[key]['male'] = float(merged[key]['count']) / float(total)
            else:
                _logger.error('failed to parse gender {0}'.format(name))
            merged[key]['count'] = total
            merged[key]['gender'] = 'A'
    return merged.values()


def _main(**kwargs):
    names = _load_directory(kwargs['name_dir'])
    if kwargs['gender'] == 'male':
        names = filter(lambda x: x['gender']=='M', names)
    elif kwargs['gender'] == 'female':
        names = filter(lambda x: x['gender']=='F', names)
    elif kwargs['gender'] == 'combined':
        names = _merge_genders(names)
    else:
        _logger.error('failed to parse gender {0}'.format(kwargs))

    _logger.info('calculating yearly stats')
    by_year = _group_by('year', names)
    year_totals = {}
    for year, year_names in by_year.iteritems():
        year_totals[year] = sum(map(operator.itemgetter('count'), year_names))
    
    # plot yearly stats
    pyplot.figure()
    pyplot.title('total births by year')
    ordered = sorted(year_totals.items(), key=operator.itemgetter(0))
    pyplot.plot(
        map(operator.itemgetter(0), ordered),
        map(operator.itemgetter(1), ordered))

    _logger.info('calculating name yearly popularity')
    for name in names:
        name['popularity'] = float(name['count']) / float(year_totals[name['year']])

    _logger.info('writing to {0}'.format(kwargs['out']))
    pickle.dump(names, open(kwargs['out'], 'w'))
    pyplot.show()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name-dir', 
        default='./names', 
        help='Directory of name data')
    parser.add_argument('gender', choices=['male', 'female', 'combined'])
    parser.add_argument('out')


    kwargs = vars(parser.parse_args())
    _logger.debug('arguments {0}'.format(kwargs))
    _main(**kwargs)

    


