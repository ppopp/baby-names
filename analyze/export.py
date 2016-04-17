import argparse
import cPickle as pickle
import json
import os
import logging

_logger = logging.getLogger(__name__)

def _group_by(field, entries):
    groups = {}
    for entry in entries:
        group = entry[field]
        if not (group in groups):
            groups[group] = []
        groups[group].append(entry)
    return groups

def _main(**kwargs):
    names = pickle.load(open(kwargs['input'], 'r'))
    by_name = _group_by('name', names)

    for name, name_data in by_name.iteritems():
        popularity = {}
        counts = {}
        gender = ''
        for entry in name_data:
            year = int(entry['year'])
            popularity[year] = entry['popularity']
            counts[year] = entry['count']
            gender = entry['gender']

        name_directory = os.path.join(kwargs['output_directory'], name[0].lower())
        if not os.path.isdir(name_directory):
            os.mkdir(name_directory)

        output_path = os.path.join(
            name_directory,
            name + '_' +  gender + '.json')

        output_data = {}
        output_data['name'] = name
        output_data['gender'] = gender
        output_data['counts'] = counts
        output_data['popularity'] = popularity

        _logger.info('writing output to {0}'.format(output_path))
        json.dump(output_data, open(output_path, 'w'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output_directory')

    kwargs = vars(parser.parse_args())
    _main(**kwargs)
