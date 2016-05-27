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
try:
  from picard import log
  inpicard = True

  # The next bit is a truly horrific hack to let this script, running as a Picard
  # plugin, access python packages installed at the system level (musicbrainzngs)
  #
  # It "works" on an OS X system with MacPorts.
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
except ImportError:
  import logging as log
  inpicard = False

import musicbrainzngs
musicbrainzngs.set_useragent("extra_relationships", PLUGIN_VERSION,\
        "extra_relationships")

def get_place_location_string(place_id):
    log.debug("%s: get_place_location_string cache size %d", PLUGIN_NAME,
            len(get_place_location_string.cache))
    if place_id in get_place_location_string.cache:
        return get_place_location_string.cache[place_id]

    place_full_info = musicbrainzngs.get_place_by_id(place_id,
            includes = ['area-rels'])['place']
    name_components = [
            place_full_info['name'], # Union Chapel
            place_full_info['area']['name'], # Islington
            ]
    
    # Now walk up the name
    def check_area(area_id):
        area_full_info = musicbrainzngs.get_area_by_id(area_id,
                includes = ['area-rels'])['area']
        for area_rel in area_full_info['area-relation-list']:
            # This type-id is "type of"
            if area_rel['type-id'] == 'de7cc874-8b1b-3a05-8272-f3834c968fb7' \
                    and 'direction' in area_rel \
                    and area_rel['direction'] == 'backward':
                name_components.append(area_rel['area']['name'])
                check_area(area_rel['area']['id'])

    check_area(place_full_info['area']['id'])

    def remove_seq_dupes(seq):
      newseq = [ ]
      for x in seq:
        if len(newseq) == 0 or newseq[-1] != x:
          newseq.append(x)
      return newseq

    place_location_string = ", ".join(remove_seq_dupes(name_components))
    get_place_location_string.cache[place_id] = place_location_string
    return place_location_string
get_place_location_string.cache = { }

def get_recording_live_string(recording_id):
    log.debug("%s: get_recording_live_string cache size %d", PLUGIN_NAME,
            len(get_recording_live_string.cache))
    if recording_id in get_recording_live_string.cache:
        return get_recording_live_string.cache[recording_id]

    recording_info = musicbrainzngs.get_recording_by_id(recording_id,
            includes = ['work-rels', 'place-rels'])['recording']
    live = False
    if 'disambiguation' in recording_info \
        and 'live' in recording_info['disambiguation']:
        live = True
    else:
        try:
            for work_rel in recording_info['work-relation-list']:
                for work_rel_attrib in work_rel['attribute-list']:
                    if work_rel_attrib == 'live':
                        live = True
                        break
        except:
            pass

    place_strings = [ ]
    if 'place-relation-list' in recording_info:
        #assert len(recording_info['place-relation-list']) == 1
        for place_rel in recording_info['place-relation-list']:
            try:
              assert place_rel['begin'] == place_rel['end']
              if len(place_rel['begin']):
                location_string = get_place_location_string(place_rel['place']['id'])
                live_loc_str = "live, " if live else "recorded, "
                live_loc_str += "%s: %s"%(place_rel['begin'], location_string)
                get_recording_live_string.cache[recording_id] = live_loc_str
                place_strings.append(live_loc_str)
            except:
              log.debug("Got confused by %s", repr(place_rel))
              pass
        place_strings.sort()
        return '; '.join(place_strings)
    return None
get_recording_live_string.cache = { }

def extra_relationships(tagger, metadata, release, track):
    recording_id = metadata['musicbrainz_recordingid']
    recording_live_string = get_recording_live_string(recording_id)
    if recording_live_string:
        old_comment = metadata.get('~recordingcomment', None)
        log.info("%s: recording id %s -> %s (%s)", PLUGIN_NAME, recording_id,
                recording_live_string, old_comment)
        metadata.add_unique('~recordinglivecomment', recording_live_string)

if inpicard:
  log.debug("%s: initalising...", PLUGIN_NAME)
  from picard.metadata import register_track_metadata_processor
  from picard.plugin import PluginPriority
  register_track_metadata_processor(extra_relationships,
          priority = PluginPriority.HIGH)
