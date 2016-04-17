import argparse
import logging
import json
import os
import codecs

import us_ss
import crunch


_logger = logging.getLogger(__name__)


def _main(**kwargs):
    names = us_ss.load(kwargs['input_directory'])

    # separate names into groups 
    male_names = filter(lambda x: x['gender']=='M', names)
    female_names = filter(lambda x: x['gender']=='F', names)
    all_names = crunch.merge_genders(names)

    # process name group (male/female) separately
    name_groups = [male_names, female_names]
    for i, name_group in enumerate(name_groups):
        _logger.info('processesing name set {0} of {1}'.format(i, len(name_groups)))
        name_group = crunch.popularity(name_group)
        crunch.write_names(name_group, kwargs['output_directory'])

    # process global information 
    _logger.info('processing all names')
    all_names = crunch.popularity(all_names)
    crunch.write_names(all_names, kwargs['output_directory'])

    # write name list
    name_set = set(map(lambda x: x['name'], all_names))
    name_list_filepath = os.path.join(kwargs['output_directory'], 'namelist.json')
    json.dump(
        {'names':list(name_set)},
        codecs.open(name_list_filepath, 'w', 'utf-8')
    )

    # write year list
    year_max_pop_filepath = os.path.join(kwargs['output_directory'], 'namecentroids.json')
    year_names_filepath = os.path.join(kwargs['output_directory'], 'yearlists.json')
    (year_max_pop, year_names) = crunch.highest_popularity(all_names)
    json.dump(
        year_max_pop,
        codecs.open(year_max_pop_filepath, 'w', 'utf-8')
    )
    json.dump(
        year_names,
        codecs.open(year_names_filepath, 'w', 'utf-8')
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_directory')
    parser.add_argument('output_directory')

    kwargs = vars(parser.parse_args())
    logging.basicConfig(level=logging.DEBUG)
    _main(**kwargs)

