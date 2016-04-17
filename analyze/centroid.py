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
            print popularity
            print denom
            print year_centroid
        if denom > 0:
            year_centroid /= denom


        centroids[name] = int(year_centroid)

    pickle.dump(centroids, open(kwargs['output'], 'w'))



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')

    kwargs = vars(parser.parse_args())
    _main(**kwargs)
