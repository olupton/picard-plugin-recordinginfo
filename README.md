# picard-plugin-recordinginfo
MusicBrainz Picard plugin that summarises recording information in file tags. The meat of it is a function `get_recording_live_string()`, which takes the MusicBrainz ID of a recording and returns a string summarising where that recording was made by following the recording relationships:
```
>>> from extra_relationships import get_recording_live_string
>>> print get_recording_live_string('ddc9a45a-e3e3-42bb-af05-ea87c17dab63')
live, 1970-02-14: University Refectory, Leeds, West Yorkshire, England, United Kingdom
```

# Requirements
This plugin uses the `musicbrainzngs` python package, which can be installed using `pip`:
```
pip install musicbrainzngs
```
Unfortunately it doesn't seem like there is a nice way of making sure that a Picard plugin has access to extra dependencies like this, so the plugin itself (`extra_relationships.py`) contains a horrible hack to give itself access to python modules installed in `/opt/local/...`.

# Installation
Place the plugin file (`extra_relationships.py`) in the Picard plugin directory (`~/.config/MusicBrainz/Picard/plugins/` on my system).

# Use
Once installed, the plugin populates a variable `_recordinglivecomment`, which  you can use in Picard's tagger script and write to a tag that is saved to your files, for example:
```
$if(%_recordinglivecomment%, $set(comment, %_recordinglivecomment%))
 ```
