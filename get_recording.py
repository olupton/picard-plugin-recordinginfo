import musicbrainzngs, pycountry
musicbrainzngs.set_useragent("recording_id_test", "0.1", "ol")

def get_place_location_string(place_id):
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
                    and 'direction' in area_rel \ # only walk UP
                    and area_rel['direction'] == 'backward':
                name_components.append(area_rel['area']['name'])
                check_area(area_rel['area']['id'])

    check_area(place_full_info['area']['id'])
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
