import operator
import logging
import os
import json
import math

_logger = logging.getLogger(__name__)

def _group_by(field, entries):
    groups = {}
    for entry in entries:
        group = entry[field]
        if not (group in groups):
            groups[group] = []
        groups[group].append(entry)
    return groups

def merge_genders(names):
    '''
    Takes male and female names and converts them to 
    a non-gendered entity
    '''
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

def yearly_stats(names):
    '''
    Calculates popularity, diversity index and rank of names and adds information to names
    '''
    _logger.info('calculating yearly stats')
    by_year = _group_by('year', names)
    year_totals = {}
    for year, year_names in by_year.iteritems():
        year_totals[year] = sum(map(operator.itemgetter('count'), year_names))

        sorted_names = sorted(names, key=operator.itemgetter('count'), reverse=True)
        cntr = 1
        last_count = sorted_names[0]['count']
        last_rank = 1
        sorted_names[0]['rank'] = 1
        for name in sorted_names[1:]:
            cntr += 1
            if name['count'] < last_count:
                name['rank'] = cntr
                last_rank = cntr
                last_count = name['count']
            else:
                name['rank'] = last_rank
    
    _logger.info('calculating name yearly popularity')
    for name in names:
        name['popularity'] = float(name['count']) / float(year_totals[name['year']])
        name['diversity_index'] = -1.0 * name['popularity'] * math.log(name['popularity'])
        if name['popularity'] > 0.0:
            name['log_popularity'] = 100.0 + (15.0 * math.log10(name['popularity']))
        else:
            name['log_popuarlity'] = 0.0

    return names

def highest_popularity(names):
    ''' 
    Calculates name year max popularity and returns a dictionary of
    years with the names as keys and a dictionary of years with lists of names
    '''
    by_name = _group_by('name', names)

    max_popularity = {}
    for name, name_data in by_name.iteritems():
        max_popularity_val = -1
        max_popularity_year = -1
        for entry in name_data:
            if entry['popularity'] > max_popularity_val:
                max_popularity_val = entry['popularity']
                max_popularity_year = entry['year']
        max_popularity[name] = max_popularity_year

    year_names = {}
    for name, year in max_popularity.items():
        if not (year in year_names):
            year_names[year] = []
        year_names[year].append(name)

    return (max_popularity, year_names)

def year_centroid(names):
    ''' 
    Calculates name year centroid and returns a dictionary of
    year centroids with the names as keys
    '''
    by_name = _group_by('name', names)

    centroids = {}
    for name, name_data in by_name.iteritems():
        popularity = {}
        counts = {}
        gender = ''
        for entry in name_data:
            year = int(entry['year'])
            popularity[year] = entry['popularity']
            counts[year] = entry['count']
            gender = entry['gender']

        # have to normalize popularity because some values are too small
        total_popularity = sum(popularity.values())
        if total_popularity <= 0.0:
            total_popularity = 1.0
        for k in popularity.keys():
            popularity[k] /= total_popularity

        year_centroid = 0.0
        denom = 0.0
        for year, val in popularity.items():
            year_centroid += float(val) * float(year)
            denom += float(val)

        final = year_centroid / denom
        if final < 1800:
            _logger.warning('error calculating centroid of "{0}"'.format(name))
        if denom > 0:
            year_centroid /= denom

        centroids[name] = int(year_centroid)
    return centroid

def write_names(names, output_directory):
    '''
    Writes basic name data to file
    '''
    by_name = _group_by('name', names)

    for name, name_data in by_name.iteritems():
        # organize name data into yearly info
        output = {
            'name': name,
            'gender': name_data[0]['gender']
        }

        for entry in name_data:
            year = int(entry['year'])
            keys = entry.keys()
            keys.remove('gender')
            keys.remove('year')
            keys.remove('name')
            for k in keys:
                value = entry[k]
                if not (k in output):
                    output[k] = {}
                output[k][year] = value

        name_directory = os.path.join(output_directory, name[0].lower())
        if not os.path.isdir(name_directory):
            os.mkdir(name_directory)

        output_path = os.path.join(
            name_directory,
            '{0}_{1}.json'.format(output['name'], output['gender']))

        _logger.debug('writing output to {0}'.format(output_path))
        json.dump(output, open(output_path, 'w'))


