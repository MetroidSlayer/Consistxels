# Reads/writes .aseprite files based on Aseprite's official documentation on the file format, found here:
# https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md

# Reading/writing the bytes in the correct spots as the correct types is done with the struct library:
# https://docs.python.org/3/library/struct.html

# Cel images are stored as PIL Image objects.

from PIL import Image
import zlib
import struct
import os

# "Magic numbers". Gonna be real - I have no idea what that means.
FILE_MAGIC_NUMBER = 0xA5E0
FRAME_MAGIC_NUMBER = 0xF1FA

# Identifiers for the different chunks. An identifier is in a chunk's header,
# and can be used to determine what the chunk contains.
OLD_PALETTE_CHUNK_1 = 0x0004 # Occasionally used in newer Aseprite versions for small palettes, including the default palette. Only contains RGB, no A
OLD_PALETTE_CHUNK_2 = 0x0011 # Almost identical to _1, but stores colors from 0-63 instead of 0-255
LAYER_CHUNK = 0x2004 # Contains things like visiblity, editability, opacity, layer name, etc.
CEL_CHUNK = 0x2005 # Contains things like position, layer index, and opacity, as well as things specific to each cel type
CEL_EXTRA_CHUNK = 0x2006 # Contains extra info for latest read cel. No idea if this is ever saved, seems like runtime info, but what do I know
COLOR_PROFILE_CHUNK = 0x2007 # Contains color profile and gamma, and can contain an ICC profile: http://www.color.org/ICC1V42.pdf
EXTERNAL_FILES_CHUNK = 0x2008 # References external files, such as palettes, tilesets, extensions
# MASK_CHUNK_DEPRECATED = 0x2016 # No info about usage is provided, but presumably stored masks and seemed to use bitmaps for it
# PATH_CHUNK_UNUSED = 0x2017 # No info is provided other than it never being used
TAGS_CHUNK = 0x2018 # Modifies animation playback for selected frames. Followed by several USER_DATA_CHUNKs.
PALETTE_CHUNK = 0x2019 # Contains the RGBA palette, and can contain names for colors
USER_DATA_CHUNK = 0x2020 # Specifies data to be associated with the previous chunk.
SLICE_CHUNK = 0x2022 # No info provided about usage, but I THINK slices are more of an editor thing than a sprite thing? I dunno
TILESET_CHUNK = 0x2023 # No info provided about usage, but definitely contains tileset info, I can tell ya that much

# Could add layer/cel types as consts, but they don't work for match statements for some reason so I don't really see a reason
# Could ALSO add them as enums, but they seem kinda hackey in Python from what I'm seeing, so idk

# Use the given path to load an .aseprite file and return the dictionary containing its data.
def load(path) -> dict:
    # Check that file is the right type (.ase or .aseprite; both are identical)
    ext = os.path.splitext(path)[1]
    if not (ext == ".ase" or ext == ".aseprite"):
        raise ValueError("File must be .ase or .aseprite")

    with open(path, "rb") as file: # Open file in read-binary mode
        data = file.read() # Read the bytes, store them
    
    return bytes_to_dict(data) # Convert the bytes to dict, and return

# Use the given dictionary to save a new .aseprite file at the given path.
def save(sprite_dict, path):
    sprite_data = dict_to_bytes(sprite_dict) # Convert the dict to bytes

    with open(path, "wb") as file: # Open file in write-binary mode
        file.write(sprite_data) # Write the bytes to the file

# Convert bytes from an .aseprite file to a Python dictionary, with the cel images as PIL Image objects.
def bytes_to_dict(data) -> dict:
    # Header mostly consists of stuff that applies to the sprite in general, or settings for thte editor
    file_header = struct.unpack("<IHHHHHIHIIB3BhhHH", data[0 : 40])

    (number_of_bytes_in_file, file_magic_number, number_of_frames_in_file, width, height,
        color_depth, flags, speed, _, _, transparency_index, _,
        pixel_width, pixel_height, grid_x_pos, grid_y_pos, grid_width, grid_height
    ) = file_header

    # TODO: split "flags" into some bools like layers_opacity_valid, layer_groups_blend_opacity_valid, layers_have_uuid

    sprite_dict = { # This is the general structure for the sprite_dicts used throughout this script
        "file_size": number_of_bytes_in_file,
        "magic_number": file_magic_number,
        "number_of_frames": number_of_frames_in_file,
        "width": width,
        "height": height,
        "color_depth": color_depth,
        "flags": flags,
        "speed": speed,
        "transparency_index": transparency_index,
        "pixel_width": pixel_width,
        "pixel_height": pixel_height,
        "grid_x_pos": grid_x_pos,
        "grid_y_pos":grid_y_pos,
        "grid_width": grid_width,
        "grid_height": grid_height,
        "frames": [] # All frames are added here; all chunks are added to their respective frames
    }

    curr_byte = 128 # The size of the header, so that the header can be skipped

    for frame_index in range(number_of_frames_in_file):
        frame_header = struct.unpack("<IHHH2BI", data[curr_byte : curr_byte + 16]) # i.e. look FROM current byte TO current byte + 16 bytes, as each header is 16 bytes
        curr_byte += 16

        (number_of_bytes_in_frame, frame_magic_number, old_number_of_chunks_in_frame,
        frame_duration, _, _, number_of_chunks_in_frame) = frame_header

        sprite_dict["frames"].append({
            "frame_size": number_of_bytes_in_frame,
            "magic_number": frame_magic_number,
            "old_number_of_chunks": old_number_of_chunks_in_frame, # Old and somewhat deprecated, but still used if the newer one (seen below) is empty
            "duration": frame_duration,
            "number_of_chunks": number_of_chunks_in_frame, # Newer, but not always used over the old one
            "chunks": []
        })

        # If the new number of chunks is empty, use the old one
        number_of_chunks_in_frame = number_of_chunks_in_frame if number_of_chunks_in_frame else old_number_of_chunks_in_frame

        for chunk_index in range(number_of_chunks_in_frame):
            chunk_header = struct.unpack("<IH", data[curr_byte : curr_byte + 6])
            chunk_byte = curr_byte # chunk_byte is used in addition to number_of_bytes_in_chunk to find next chunk location
            curr_byte += 6

            number_of_bytes_in_chunk, chunk_type = chunk_header

            chunk_dict = {
                "chunk_size": number_of_bytes_in_chunk,
                "chunk_type": chunk_type
            }

            # Chunks are usually cels that contain images, but for the first frame, they also contain layers, palette, color profile, etc.
            # if chunk_type == OLD_PALETTE_CHUNK_1 or chunk_type == OLD_PALETTE_CHUNK_2: # OLD_PALETTE_CHUNK_2 is almost identical to _1, just measures colors from 0-63 instead of 0-255.
            #     number_of_packets = struct.unpack("<H", data[curr_byte : curr_byte + 2])[0]
            #     curr_byte += 2

            #     chunk_dict.update({"packets": []})

            #     for _ in range(number_of_packets):
            #         packet_data = struct.unpack("<BB", data[curr_byte : curr_byte + 2])
            #         curr_byte += 2

            #         number_of_palette_entries_to_skip, number_of_colors_in_packet = packet_data

            #         entries : list[tuple[int, int, int]] = []
                    
            #         for _ in range(number_of_colors_in_packet):
            #             palette_entry_data = struct.unpack("<BBB", data[curr_byte : curr_byte + 3])
            #             curr_byte += 3

            #             # Technically, since it's already a tuple, I can just append it to "entries", right?
            #             # r, g, b = palette_entry_data

            #             # palette_entry_data contains Red, Green, and Blue; they're already in a tuple, so no need to separate them first
            #             entries.append(palette_entry_data)
                    
            #         chunk_dict["packets"].append({
            #             "number_of_palette_entries_to_skip": number_of_palette_entries_to_skip,
            #             "entries": entries
            #         })
            # elif chunk_type == OLD_PALETTE_CHUNK_2:
            #     pass
            if chunk_type == LAYER_CHUNK:
                # Layer flags are stored as a single int. For usability, they're separated into individual bools here.                
                layer_flags = struct.unpack("<H", data[curr_byte : curr_byte + 2])[0]
                curr_byte += 2

                layer_visible = layer_flags & 1 == 1
                layer_editable = layer_flags & 2 == 2
                layer_lock_movement = layer_flags & 4 == 4
                layer_background = layer_flags & 8 == 8
                layer_prefer_linked_cells = layer_flags & 16 == 16
                layer_group_collapsed = layer_flags & 32 == 32
                layer_reference_layer = layer_flags & 64 == 64

                layer_data = struct.unpack("<HHHHHB3BH", data[curr_byte : curr_byte + 16])
                curr_byte += 16

                (layer_type, layer_child_level, _, _,
                    layer_blend_mode, layer_opacity, _, _, _, layer_name_size) = layer_data

                layer_name = data[curr_byte : curr_byte + layer_name_size].decode('utf-8') # Layer's name is a string that must be decoded
                curr_byte += layer_name_size

                chunk_dict.update({
                    "visible": layer_visible,
                    "editable": layer_editable,
                    "lock_movement": layer_lock_movement,
                    "background": layer_background,
                    "prefer_linked_cells": layer_prefer_linked_cells,
                    "group_collapsed": layer_group_collapsed,
                    "reference_layer": layer_reference_layer,
                    "layer_type": layer_type,
                    "child_level": layer_child_level,
                    "blend_mode": layer_blend_mode,
                    "opacity": layer_opacity,
                    "name": layer_name
                })

            elif chunk_type == CEL_CHUNK:
                cel_data = struct.unpack("<HhhBHh", data[curr_byte : curr_byte + 11])
                curr_byte += 16

                cel_layer_index, cel_x_pos, cel_y_pos, cel_opacity, cel_type, cel_zindex = cel_data

                chunk_dict.update({
                    "chunk_size": number_of_bytes_in_chunk,
                    "chunk_type": chunk_type,
                    "layer_index": cel_layer_index,
                    "x_pos": cel_x_pos,
                    "y_pos": cel_y_pos,
                    "opacity": cel_opacity,
                    "cel_type": cel_type,
                    "z_index": cel_zindex
                })

                cel_image = None

                match cel_type:
                    case 0: # Raw image data
                        cel_width, cel_height = struct.unpack("<HH", data[curr_byte : curr_byte + 4])
                        curr_byte += 4

                        # Bytes are not compressed, and can immediately be used
                        cel_pixels = data[curr_byte : chunk_byte + number_of_bytes_in_chunk]
                        cel_image = Image.frombytes("RGBA", (cel_width, cel_height), cel_pixels)

                        chunk_dict.update({
                            "width": cel_width, "height": cel_height, "image": cel_image
                        })
                    case 1: # Linked cel
                        cel_frame_to_link = struct.unpack("<H", data[curr_byte : curr_byte + 2])[0]
                        curr_byte += 2
                        chunk_dict.update({
                            "frame_position_to_link_with": cel_frame_to_link
                        })
                    case 2: # Compressed image
                        cel_width, cel_height = struct.unpack("<HH", data[curr_byte : curr_byte + 4])
                        curr_byte += 4

                        # Bytes are compressed, and must be decompressed before they can be used
                        cel_pixels_compressed = data[curr_byte : chunk_byte + number_of_bytes_in_chunk]
                        cel_pixels = zlib.decompress(cel_pixels_compressed)
                        cel_image = Image.frombytes("RGBA", (cel_width, cel_height), cel_pixels)

                        chunk_dict.update({
                            "width": cel_width, "height": cel_height, "image": cel_image
                        })
                    case 3: # Compressed tilemap
                        compressed_tilemap_data = struct.unpack("<HHHIIII", data[curr_byte : curr_byte + 22])
                        curr_byte += 32 # 22 as seen above, plus 10 for reserved bytes
                        cel_width_tiles, cel_height_tiles, bits_per_tile, bitmask_for_tile_ID, bitmask_x_flip, bitmask_y_flip, bitmask_diagonal_flip = compressed_tilemap_data
                        tile_bytes = data[curr_byte : chunk_byte + number_of_bytes_in_chunk] # TODO actually unpack at some point

                        chunk_dict.update({
                            "width_tiles": cel_width_tiles, # The width, in tiles
                            "height_tiles": cel_height_tiles, # The height, in tiles
                            "bits_per_tile": bits_per_tile,
                            "bitmask_for_tile_ID": bitmask_for_tile_ID,
                            "bitmask_x_flip": bitmask_x_flip,
                            "bitmask_y_flip": bitmask_y_flip,
                            "bitmask_diagonal_flip": bitmask_diagonal_flip,
                            "tile_bytes": tile_bytes
                        })
            
            # TODO: add handling for other chunk types.
            # elif chunk_type == CEL_EXTRA_CHUNK:
            #     pass
            
            elif chunk_type == COLOR_PROFILE_CHUNK:
                color_profile_data = struct.unpack("<HHf", data[curr_byte : curr_byte + 8])
                curr_byte += 8
                # then 8 bytes, then ICC. TODO handle ICC

                color_profile_type, color_profile_flags, color_profile_fixed_gamma = color_profile_data

                chunk_dict.update({
                    "color_profile_type": color_profile_type,
                    "use_special_fixed_gamma": color_profile_flags > 0,
                    "fixed_gamma": color_profile_fixed_gamma
                })

                if color_profile_type == 2: # i.e. if color profile uses ICC profile:
                    icc_data_length = struct.unpack("<I", data[curr_byte : curr_byte + 4])[0]
                    curr_byte += 4
                    
                    # Presumably, ICC data takes up all the rest of the chunk. Packing/unpacking the ICC data will probably
                    # take a lotta work, it's a whole 'nother data type and documentation, so I'm not going to bother right now.
                    icc_data_bytes = data[curr_byte : chunk_byte + number_of_bytes_in_chunk]

                    chunk_dict.update({
                        "icc_data_length": icc_data_length,
                        "icc_data_bytes": icc_data_bytes
                    })

            # TODO: add handling for other chunk types.
            # elif chunk_type == EXTERNAL_FILES_CHUNK:
            #     pass
            # elif chunk_type == TAGS_CHUNK:
            #     pass
            elif chunk_type == PALETTE_CHUNK:
                palette_data = struct.unpack("<III", data[curr_byte : curr_byte + 12])
                curr_byte += 20 # 12 for above data, + 8 for unused bytes

                number_of_entries_in_palette, first_color_index_to_change, last_color_index_to_change = palette_data
                
                chunk_dict.update({
                    "number_of_entries": number_of_entries_in_palette,
                    "first_color_index_to_change": first_color_index_to_change, # i have NO IDEA what this means
                    "last_color_index_to_change": last_color_index_to_change,
                    "entries": []
                })

                for _ in range(number_of_entries_in_palette):
                    palette_entry_data = struct.unpack("<HBBBB", data[curr_byte : curr_byte + 6])
                    curr_byte += 6

                    palette_entry_flags, r, g, b, a = palette_entry_data # r, g, b, a: channels for a color

                    palette_entry_dict = {
                        "color": (r, g, b, a)
                    }

                    if palette_entry_flags > 1:
                        palette_entry_name_data = struct.unpack("<H", data[curr_byte : curr_byte + 2])
                        curr_byte += 2

                        palette_entry_name_size = palette_entry_name_data[0]
                        palette_entry_name = data[curr_byte : curr_byte + palette_entry_name_size].decode('utf-8')
                        curr_byte += palette_entry_name_size

                        palette_entry_dict.update({"name": palette_entry_name})
                    
                    chunk_dict["entries"].append(palette_entry_dict)

            # elif chunk_type == USER_DATA_CHUNK:
            #     pass
            # elif chunk_type == SLICE_CHUNK:
            #     pass
            # elif chunk_type == TILESET_CHUNK:
            #     pass

            else: # If an unhandled chunk type, just pass along the bytes
                chunk_dict.update({
                    "chunk_bytes": data[curr_byte : chunk_byte + number_of_bytes_in_chunk] # All the rest of the data in the chunk as bytes
                })

            sprite_dict["frames"][frame_index]["chunks"].append(chunk_dict)

            # Set the curr_byte manually to the next known chunk, as it's possible that it's not yet pointing to the actual end of the chunk.
            curr_byte = chunk_byte + number_of_bytes_in_chunk 
    
    return sprite_dict # Return dict containing usable info

# Convert the given dictionary to bytes, to be saved or otherwised used later.
def dict_to_bytes(sprite_dict) -> bytearray:
    file_bytes : bytearray # The entire file's bytes. (Could move to later)
    file_data_bytes : bytearray = bytearray() # Byte array that will contain frame data, to be appended to file header later.

    number_of_colors_in_palette = 1

    for frame in sprite_dict["frames"]:
        frame_bytes : bytearray
        frame_data_bytes : bytearray = bytearray() # Byte array that will contain chunk data, to be appended to frame header later.

        for chunk in frame.get("chunks", []):
            chunk_type = chunk["chunk_type"]
            chunk_bytes : bytearray
            chunk_data_bytes : bytearray

            if chunk_type == LAYER_CHUNK:
                # Layer flags use a single int, but dict stores them as individual bools
                layer_flags = 0
                layer_flags += 1 if chunk.get("visible", True) else 0
                layer_flags += 2 if chunk.get("editable", True) else 0
                layer_flags += 4 if chunk.get("lock_movement", False) else 0
                layer_flags += 8 if chunk.get("background", False) else 0
                layer_flags += 16 if chunk.get("prefer_linked_cells", False) else 0
                layer_flags += 32 if chunk.get("group_collapsed", False) else 0
                layer_flags += 64 if chunk.get("reference_layer", False) else 0

                layer_type = chunk.get("layer_type", 0)
                layer_child_level = chunk.get("child_level", 0)
                layer_blend_mode = chunk.get("blend_mode", 0)
                layer_opacity = chunk.get("opacity", 255)

                chunk_data_bytes = bytearray(struct.pack("<HHHHHHB",
                    layer_flags, layer_type, layer_child_level,
                    0, 0, # layer width/height, unused
                    layer_blend_mode, layer_opacity
                ))

                chunk_data_bytes += bytes(3) # unused bytes

                chunk_name_bytes = bytearray(chunk.get("name", "").encode('utf-8'))
                chunk_data_bytes += struct.pack("<H", len(chunk_name_bytes))
                chunk_data_bytes += chunk_name_bytes
            elif chunk_type == CEL_CHUNK:
                cel_layer_index = chunk.get("layer_index", 0)
                cel_x_pos = chunk.get("x_pos", 0)
                cel_y_pos = chunk.get("y_pos", 0)
                cel_opacity = chunk.get("opacity", 255)
                cel_type = chunk.get("cel_type", 2)
                cel_zindex = chunk.get("z_index", 0)

                cel_type_bytes : bytearray # bytes will hold varying info, as the different types contain different things

                match cel_type: # TODO implement other things
                    case 0: # Raw image data
                        cel_image : Image.Image = chunk.get("image", None)

                        if cel_image != None:
                            bbox = cel_image.getbbox()
                            cel_image = cel_image.crop(bbox) 

                            cel_width = cel_image.size[0]
                            cel_height = cel_image.size[1]

                            cel_pixels = cel_image.tobytes()

                            cel_type_bytes = bytearray(struct.pack("<HH", cel_width, cel_height))
                            cel_type_bytes += cel_pixels
                        else:
                            cel_image = Image.new("RGBA", (0,0), (0,0,0,0))
                            cel_width = 0
                            cel_height = 0
                            cel_x_pos = 0
                            cel_y_pos = 0
                            cel_type_bytes = bytearray(struct.pack("<HH", cel_width, cel_height))
                    case 1: # Linked cel
                        cel_frame_to_link = chunk.get("frame_position_to_link_with", 0)
                        cel_type_bytes = bytearray(struct.pack("<H", cel_frame_to_link))
                    case 2: # Compressed image
                        cel_image : Image.Image = chunk.get("image", None) # Get the image
                        
                        if cel_image != None:
                            bbox = cel_image.getbbox() # Get the bbox

                            cel_image = cel_image.crop(bbox) # In order to save on file size, crop the image

                            cel_width = cel_image.size[0]
                            cel_height = cel_image.size[1]

                            cel_x_pos += bbox[0] # Increase x and y pos to match new crop
                            cel_y_pos += bbox[1]

                            cel_pixels = cel_image.tobytes() # Get image bytes
                            cel_pixels_compressed = zlib.compress(cel_pixels) # Images are compressed w/ zlib to save on file size

                            cel_type_bytes = bytearray(struct.pack("<HH", cel_width, cel_height))
                            cel_type_bytes += cel_pixels_compressed
                        else: # If cel is empty, which it SHOULDN'T be if it exists, so this is probably unnecessary
                            cel_image = Image.new("RGBA", (0,0), (0,0,0,0))
                            cel_width = 0
                            cel_height = 0
                            cel_x_pos = 0
                            cel_y_pos = 0

                            cel_type_bytes = bytearray(struct.pack("<HH", cel_width, cel_height))
                    case 3: # Compressed tilemap
                        pass # TODO
                
                chunk_data_bytes = bytearray(struct.pack("<HhhBHh5B",
                    cel_layer_index, cel_x_pos, cel_y_pos, cel_opacity, cel_type, cel_zindex,
                    0, 0, 0, 0, 0 # unused
                ))

                # Could get rid of the unused bytes above and just add 5 bytes for simplicity I think

                chunk_data_bytes += cel_type_bytes

            elif chunk_type == COLOR_PROFILE_CHUNK: # TODO some sort of check that requires an .aseprite to have all chunks necessary to be valid?

                color_profile_type = chunk.get("color_profile_type", 1)
                
                color_profile_flags = 0
                color_profile_flags += 1 if chunk.get("use_special_fixed_gamma", False) else 0

                color_profile_fixed_gamma = chunk.get("fixed_gamma", 0.0)

                chunk_data_bytes = bytearray(struct.pack("<HHf8B",
                    color_profile_type, color_profile_flags, color_profile_fixed_gamma,
                    0, 0, 0, 0, 0, 0, 0, 0
                ))
                
                if color_profile_type == 2: # If ICC color profile:
                    icc_data_length = chunk.get("icc_data_length")
                    icc_data_bytes = chunk.get("icc_data_bytes")

                    chunk_data_bytes += bytearray(struct.pack("<I", icc_data_length))
                    chunk_data_bytes += icc_data_bytes # TODO change if/when I get around to fully implementing ICC
            elif chunk_type == PALETTE_CHUNK:
                
                # TODO clean up and get rid of duplicate work. I COULD streamline this a lot but I'm pretty tired of bytes n stuff
                entries = chunk.get("entries", [])
                # What if len(entries) and number_of_colors_in_palette don't match? idk
                # for entry in entries:
                # number_of_colors_in_palette = max(chunk.get("number_of_entries", len(entries)), 1) # AT LEAST 1 entry in the palette
                number_of_colors_in_palette = chunk.get("number_of_entries", len(entries))
                # first_color_index_to_change = 0
                # last_color_index_to_change = 0

                if len(entries) and len(entries) == number_of_colors_in_palette:
                    first_color_index_to_change = chunk.get("first_color_index_to_change", 0)
                    last_color_index_to_change = chunk.get("last_color_index_to_change", (number_of_colors_in_palette - 1))

                    chunk_data_bytes = bytearray(struct.pack("<III", number_of_colors_in_palette, first_color_index_to_change, last_color_index_to_change))
                    chunk_data_bytes += bytes(8) # unused bytes

                    for entry in entries:
                        # TODO check for name!
                        chunk_data_bytes += bytearray(struct.pack("<HBBBB", 0, *entry.get("color"))) # no idea if this will work
                else:
                    chunk_data_bytes = chunk_data_bytes = bytearray(struct.pack("<III", 1, 0, 0))
                    chunk_data_bytes += bytes(8) # unused bytes
                    chunk_data_bytes += bytearray(struct.pack("<HBBBB", 0, 0, 0, 0, 0))

                # chunk_data_bytes += bytearray(struct.pack("<HBBBB", 0, 0, 0, 0, 0))
            else:
                # If an unhandled chunk type, simply add the byte data
                chunk_data_bytes = bytearray(chunk.get("chunk_bytes"))
            
            # Could move definitions here (or equivalent for other bytearrays). Not for EVERYTHING, but for most things.
            chunk_bytes = bytearray(struct.pack("<IH",
                len(chunk_data_bytes) + 6, # chunk size
                chunk_type
            ))

            chunk_bytes += chunk_data_bytes
            frame_data_bytes += chunk_bytes

        frame_bytes = bytearray(struct.pack("<IHHH2BI",
            len(frame_data_bytes) + 16, # Frame size
            FRAME_MAGIC_NUMBER,
            len(frame["chunks"]), # Old number of chunks (not unused, I think)
            frame.get("duration", 100), # Frame duration, in milliseconds
            0, 0, # Unused
            len(frame["chunks"]) # New number of chunks
        ))

        frame_bytes += frame_data_bytes
        file_data_bytes += frame_bytes
    
    # File header
    file_bytes = bytearray(struct.pack("<IHHHHHIHIIB3BHBBhhHH",
        len(file_data_bytes) + 128, # File size (all frames & chunks, plus header size)
        FILE_MAGIC_NUMBER, len(sprite_dict["frames"]),
        sprite_dict["width"], sprite_dict["height"],
        sprite_dict.get("color_depth", 32), sprite_dict.get("flags", 1),
        sprite_dict.get("speed", 100), 0, 0, sprite_dict.get("transparency_index", 0),
        0, 0, 0, # unused
        number_of_colors_in_palette,
        0, 0, # pixel width/height (default to 1:1 if either are 0)
        sprite_dict.get("grid_x_pos", 0), sprite_dict.get("grid_y_pos", 0),
        sprite_dict.get("grid_width", 16), sprite_dict.get("grid_height", 16) # Default Aseprite grid size is 16x16
    ))

    file_bytes += bytes(84) # Unused bytes

    file_bytes += file_data_bytes # Add frame bytes (which already contain chunk bytes) to file bytes, and we're done

    return file_bytes # Return completed file

# Convert a list of basic dicts that contain images and names to a valid dict that can be saved.
def format_simple_dicts(size, layer_dicts : list[dict], cel_dicts : list[dict]) -> dict:
    # Check to ensure that none of the provided layer indexes are out of range for layer_dict
    for i, cel in enumerate(cel_dicts):
        cel_layer_index = cel.get("layer_index")
        if cel_layer_index != None:
            if cel_layer_index > len(layer_dicts):
                raise IndexError(f"Cel {i}'s provided layer index is out of provided layer_dict's range")
    
    # Check to ensure that there are not fewer layers than there are cels. Therefore, only works for a file with a single frame.
    if len(layer_dicts) < len(cel_dicts):
        raise IndexError("There cannot be more cels than there are layers")

    # All layers and cels are the same things - "chunks" - and go inside frames, in this case the first frame.
    layers = [{
        "chunk_type": LAYER_CHUNK,
        "visible": layer.get("visible", True),
        "editable": layer.get("editable", True),
        "layer_type": layer.get("layer_type", 0),
        "child_level": layer.get("child_level", 0),
        "name": layer["name"]
    } for layer in layer_dicts]

    cels = [{
        "chunk_type": CEL_CHUNK,
        "layer_index": cel.get("layer_index", i), # If some manual sorting's been done, use that instead. Otherwise, use natural order.
        "cel_type": cel.get("cel_type", 2),
        "z_index": cel.get("z_index", 0),
        "image": cel["image"], # TODO better handling for other cel types (I mean not really? Like, it's not like I'll be using anything OTHER than cel_type 2 here)
    } for i, cel in enumerate(cel_dicts)]

    # This is the minimal info for a sprite to be able to work with dict_to_bytes(). All the other critical information is provided there.
    return {
        "width": size[0], "height": size[1],
        "frames": [
            {
                "chunks": [{"chunk_type": COLOR_PROFILE_CHUNK}, {"chunk_type": PALETTE_CHUNK}] + layers + cels
            }
        ]
    }

# Using layer_data taken from a saved .json, create a sprite_dict that can be saved to .aseprite.
# (Somewhat limited, as it requires images that are saved to paths.)
def layer_data_to_dict(layer_data : list[dict]): # TODO TODO TODO NOT FINISHED YET
    layer_dict = []
    cel_dict = []
    for i, layer_datum in enumerate(layer_data):
        cel_image : Image.Image = None
        
        path = layer_datum.get("search_image_path")

        if path:
            with Image.open(path) as img:
                cel_image = img.copy()
            
            bbox = cel_image.getbbox()
            bound_image = cel_image.crop(bbox) 

            cel_dict.append({
                "image": bound_image,
                "width": bound_image.size[0],
                "height": bound_image.size[1],
                "x_pos": bbox[0],
                "y_pos": bbox[1]
            })
    
    raise NotImplementedError

# # Checks if the given dict has all chunks necessary for basic use in Aseprite. If it does, returns the unmodified dict. If not, adds them to the dict and returns it.
# def check_necessary_chunks(sprite_dict) -> dict:
#     # Ensure that the first frame has a color profile chunk in index 0
#     color_profile_chunks = get_all_chunks_of_type(sprite_dict, COLOR_PROFILE_CHUNK)
#     if not color_profile_chunks: sprite_dict["frames"][0]["chunks"].insert(0, {"chunk_type": COLOR_PROFILE_CHUNK}) # does any more NEED to be done??? idk

#     # Ensure that the first frame has a palette chunk in index 1
#     palette_chunks = get_all_chunks_of_type(sprite_dict, PALETTE_CHUNK)

#     # Ensure that the first frame has at least one layer chunk, starting in index 2 (TODO: check if anything could theoretically be before??? idk)
#     layer_chunks = get_all_chunks_of_type(sprite_dict, LAYER_CHUNK)

#     return sprite_dict
# PROBABLY not going to implement this but it COULD be helpful

# Return a list containing all chunks that have a type matching the given type.
def get_all_chunks_of_type(sprite_dict, chunk_type) -> list[dict]:
    return [chunk for chunk in sprite_dict["frames"][0]["chunks"] if chunk["chunk_type"] == chunk_type]

# Return a list of all PIL images stored in the dict's frames' cels.
# TODO reconfigure for more than just cel type 2
def get_cel_images(sprite_dict) -> list[Image.Image]:
    return [chunk.get("image") for chunk in sprite_dict["frames"][0]["chunks"] if (chunk["chunk_type"] == CEL_CHUNK and (chunk["cel_type"] == 0 or chunk["cel_type"] == 2))]