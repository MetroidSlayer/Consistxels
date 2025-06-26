# The version is stored in the .json outputs so future versions can know exactly how to interpret old, outdated data

# Pre-release version info (none of these are actually supported, nor are they publically available. TODO: get rid of for public release. well i guess not? it doesnt really matter? idk):
# 0.1: very old; rudimentary and inconsistent jsons per use case
# 0.2: all mislabeled as 0.1, because I forgot to update this number. generally consistent per use case, but outdated and may not contain all info
# 0.3: now contains layer_index in limb_data
# 0.4: added "type" in header; this generally replaces "paths_are_local", prevents invalid jsons from going where they shouldn't,
#      allows for more specificities in the future, etc.

# Release version info:
# 1.0: does not exist yet

consistxels_version = "0.4"

# Info on "type" in output json header:
# "sheetdata_generated": data on the entire sprite sheet that was generated through menu_layerselect, alongside pose images.
# "layerselect_save_json": data saved in menu_layerselect; just the .json, with no images.
# "layerselect_save_folder": data saved in menu_layerselect; the .json alongside the layer images.
# "posedata_manual": not implemented yet. the user will be able to manually select poses to search at some point, and will be able to save the selected poses
#                    (will probably be renamed)