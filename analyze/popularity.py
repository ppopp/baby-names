import cPickle as pickle
import argparse
import operator
from matplotlib import pyplot

_min_year = 1880
_max_year = 2014

def _group_by(field, entries):
    groups = {}
    for entry in entries:
        group = entry[field]
        if not (group in groups):
            groups[group] = []
        groups[group].append(entry)
    return groups

def _sort_by(field, entries):
    entries = map(lambda x: (x[field], x), entries)
    entries = sorted(entries, key=operator.itemgetter(0))
    return map(operator.itemgetter(1), entries)


def _main(**kwarg):
    names = pickle.load(open(kwargs['in'], 'r'))
    by_name = _group_by('name', names)

    stats = by_name.get(kwargs['name'])
    stats = _sort_by('year', stats)

    pyplot.figure()
    pyplot.title('popularity by year')
    
    # TODO fill in missing years


    pyplot.plot(
        map(operator.itemgetter('year'), stats),
        map(operator.itemgetter('popularity'), stats))
    pyplot.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in')
    parser.add_argument('name')

    kwargs = vars(parser.parse_args())
    _main(**kwargs)


