# -*- coding: utf-8 -*-

PLUGIN_NAME = u'Add extra relationships'
PLUGIN_AUTHOR = u'Olli Lupton'
PLUGIN_DESCRIPTION = u'''Scrapes extra relationship information that you might
want to add to tagged files.
'''
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ["1.3.0"]
PLUGIN_LICENSE = "GPL-2.0"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"

import re
from picard import log
from picard.metadata import register_track_metadata_processor
import sys
sys.path = [ ]
root = '/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/'
sys.path.append(root + 'python27.zip')
root += 'python2.7'
for x in ['','site-packages','lib-dynload', 'plat-darwin', 'plat-mac',
        'plat-mac/lib-scriptpackages', 'lib-tk', 'lib-old','lib-dynload']:
    p = root
    if len(x):
         p += '/' + x
    sys.path.append(p)


for x in sys.path:
    print x

import musicbrainzngs, pycountry
musicbrainzngs.set_useragent("extra_relationships", PLUGIN_VERSION,\
        "extra_relationships")

def get_place_location_string(place_id):
    if place_id in get_place_location_string.cache:
        return get_place_location_string.cache[place_id]

    place_full_info = musicbrainzngs.get_place_by_id(place_id)['place']
    name_components = [ ]
    name_components.append(place_full_info['name']) # Union Chapel
    name_components.append(place_full_info['area']['name']) # Islington
    if 'disambiguation' in place_full_info \
            and len(place_full_info['disambiguation']):
        name_components.append(place_full_info['disambiguation']) # London
        
    place_countries = set()
    try:
        for area_code in place_full_info['area']['iso-3166-2-code-list']:
            # name, alpha2, alpha3
            area = pycountry.subdivisions.get(code=area_code)
            place_countries.add(area.country.alpha2) # GB
    except:
        print "Couldn't loop over country codes."
        print "place_full_info:"
        print place_full_info
        raise
    assert len(place_countries) == 1
    name_components.append(list(place_countries)[0])
    place_location_string = ", ".join(name_components)
    get_place_location_string.cache[place_id] = place_location_string
    return place_location_string
get_place_location_string.cache = { }

def get_recording_live_string(recording_id):
    recording_info = musicbrainzngs.get_recording_by_id(recording_id,
            includes = ['work-rels', 'place-rels'])['recording']
    live = False
    for work_rel in recording_info['work-relation-list']:
        for work_rel_attrib in work_rel['attribute-list']:
            if work_rel_attrib == 'live':
                live = True
                break
    if live:
        assert len(recording_info['place-relation-list']) == 1
        for place_rel in recording_info['place-relation-list']:
            assert place_rel['begin'] == place_rel['end']
            location_string = get_place_location_string(place_rel['place']['id'])
            live_loc_str = "live, %s: %s"%(place_rel['begin'], location_string)
            return live_loc_str

def extra_relationships(album, metadata, *args):
    recording_id = metadata['musicbrainz_recordingid']
    recording_live_string = get_recording_live_string(recording_id)
    log.debug("%s: recording id %s -> %s (%s)", PLUGIN_NAME, recording_id,
            recording_live_string, metadata['disambiguation'])
        #          )
        #for instrument in instruments:
        #    newkey = '%s:%s' % (mainkey, instrument)
        #    for value in values:
        #        metadata.add_unique(newkey, value)
        #del metadata[key]
        #pass

log.debug("%s: initalising...", PLUGIN_NAME)
from picard.plugin import PluginPriority
register_track_metadata_processor(extra_relationships)
