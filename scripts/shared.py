# The version is stored in the .json outputs so future versions can know exactly how to interpret old data that may be formatted differently.
# If and when such formatting differences happen, I'll write information about them in detail here.

consistxels_version = "1.0.1"

# Info on "type" in output json header:
# "sheetdata_generated": data on the entire sprite sheet that was generated through menu_layerselect, alongside pose images.
# "layerselect_save_json": data saved in menu_layerselect; just the .json, with no images.
# "layerselect_save_folder": data saved in menu_layerselect; the .json alongside the layer images.
# "posedata_manual": not implemented yet. the user will be able to manually select poses to search at some point, and will be able to save the selected poses.
#                    (will probably be renamed)