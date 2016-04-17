import Levenshtein
import argparse
import logging
import string
import operator
import cPickle as pickle

_logger = logging.getLogger(__name__)

def _main(**kwargs):
    name = kwargs['name'].lower()
    all_names = pickle.load(open(kwargs['name_path'], 'r'))
    all_names = set(map(string.lower, all_names))

    distances = map(lambda x: (Levenshtein.ratio(x, name), x), all_names)
    nearest = sorted(distances, key=operator.itemgetter(0), reverse=True)

    print 'similar names\n\n'
    to_show = nearest[0:kwargs['N']]
    for similar_name in to_show:
        print '\t' + similar_name[1].capitalize()

    print '\n\ncontains name\n\n'
    part_name = []
    for n in all_names:
        if name in n:
            print '\t' + n.capitalize()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-N', type=int, default=25)
    parser.add_argument('name_path')
    parser.add_argument('name')

    kwargs = vars(parser.parse_args())
    _main(**kwargs)

