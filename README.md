# Consistxels

A tool for more consistent pixel art.

_<sup>If you need to, pronounce it "Consixels" - it's much easier to say. I would've just named it that, but it's less obvious what it's supposed to do that way.</sup>_

"~~Fear~~ **_Inconsistency_ is the little-death that brings total obliteration...**"\
_- Dune Atreides, 20XX_

...well, maybe not obliteration, but certainly dissatisfaction and subpar sprites at the very least.

I hate knowing that one pixel on one pose on a sprite sheet is out-of-place, but I might hate copying and pasting every limb from every layer to double-check even more. The solution was *obviously* to create an entire program to automatically distill a sprite sheet into JSON data, detect identical poses in a given layer, and do all that copying and pasting for me.

This program _should_ work for any given sprite sheet as long as it's formatted properly, but was originally made to work with the Super Metroid Samus sprite sheet used in [SpriteSomething](https://github.com/Artheau/SpriteSomething). Check it out if you're interested.

### What it can do:
- Find poses on a sprite sheet, either by looking for pose boxes on a border, or by searching set spaces in a uniform pattern
- Save discovered pose data to one .json file, and save pose images to many, many individual .png files
- Update every instance of a given pose once the relevant pose image has been modified
- Export .png files containing layers with updated poses
- Export .png files containing layers with only _unique_ poses - useful for modifying and updating multiple pose images at once
- Some small bonus functions, like verifying whether or not two inputted images are identical, helpful for making sure your sprites are as consistent as you'd hoped

### What it _can't_ do:
- Draw your sprite art for you. Realistically, there's an upper limit to how much time this program can save

## Future planned functionality:
- Currently, common multi-layer filetypes (i.e. .tiff, .psd, .aseprite) are not supported, so you'll need to export each layer as its own image, which is a bit clunky and time-consuming. Next update, you should be able to:
    - Import multi-layered files when searching for pose data
    - Export updated layers to multi-layered filetypes
- All generated poses and images have automatically-generated names, and at the moment, renaming any of these will usually break things. Next update will feature a way to rename poses and images, as well as add layers and poses manually post-generation. This should ease clarity when opening images for editing or when sharing generated data with others.
- Not every sprite sheet has even spacing or a perfect border. Next update will feature a way to select poses on a sprite sheet manually, allowing images to be searched no matter how they're formatted. Support for irregularly-sized pose boxes during border searches will also happen at some point.

If you notice any bugs, feel free to open an issue or reach out to me on Discord (my username is mattroid9313 - not sure how to link it properly, though.) Same goes for requesting new features; if you think something might be helpful, I'd love to hear it.

# Tutorial

I've found it difficult to actually explain what this thing does or why you should use it. I hope I've done okay so far, but now I'll go in-depth with some examples.

## Editing existing pose images:

_NOTE: if you **do not yet have pose data**, go to the "Generating pose data" section first._

### Method 1:

This method should be easy-to-understand, but I find it tedious and time-consuming.

1. Open pose images in an external editor and make edits. (Depending on how many pose images there are, opening each individually can be VERY ANNOYING! If you find this tedious, try Method 2 instead. Future versions will have a better workflow.)
2. In the Consistxels main menu, in the "Load & Export Sprite Sheet with Pose Data" section, load a pose data file (in .json format, generated beforehand).
3. Select which layers you want to export, and whether you want them to be merged into a single image, or whether you'd prefer multiple individual layers.
4. Select an output folder and export. Shouldn't take long at all. (Images will be named something like "export_{sprite sheet name}_{layer name, or just "sheet" if it's all merged into one}")

From here, check the exported image, if you want - every single instance of the pose images you modified should be updated across the entire sheet! (If one or more instances *isn't* updated, check your original unmodified pose images and find the offending images - chances are, there are duplicates. This happens when the program does not identify these duplicates as identical during the generation process; this can either be because there were differences in the art that you didn't notice, or because the layers and poses are not separated as effectively as they could be. Either way, it's not a huge deal - you can update the duplicate pose image as well, or make changes to the duplicates to ensure subsequent generations will detect them as identical.)

### Method 2:

This method is faster and lets you update many pose images at once! ...But at the moment, it's kinda unintuitive. I'll work on that.

1. In the Consistxels main menu, in the "Load & Export Sprite Sheet with Pose Data" section, load a pose data file (in .json format, generated beforehand).
2. Select the layers you want to export, and select the "Individual layer image(s)" export type.
3. Select the "Only show unique pose images" checkbox.
4. Select an output folder and export.
5. Open these new layer images in an external editor, and make changes to the various poses scattered about the sprite sheet.
6. Return to Consistxels, and select the "Update pose images" export type.
7. On the left, select the now-modified layer images. (If you leave an input field empty, that layer will be skipped.)
8. Export again. After the export finishes, every pose image will have updated according to the layer images you modified.
9. **Deselect** the "Only show unique pose images" checkbox.
10. Select any export type other than "Update pose images", and select which layers to export.
11. Export one last time.

Once again, every single instance of the modified pose images should be updated, with the same caveat as before.

## Generating new pose data:

_NOTE: if you **already have pose data**, you can skip this section completely! This only matters if you want to make edits to a fully- or mostly-completed sprite sheet that does not yet have pose data._

1. **Format your sprite sheet**
    - Go through your sprite sheet, ensuring that every pose is separate, and every limb (or whatever your character has) is actually identical to every other limb like it. Even the smallest, most minute differences will cause the program to identify them as completely different pose images. If possible, remove such differences; if doing so would change the art in any meaningful way, and you want to avoid doing that, you'll just have to deal with needing to edit multiple similar-looking pose images later.
    - Export each layer as its own image file.
    - If the sprites are separated by a border, make sure that border is a SINGLE color, without any variation. Also, **make sure** pose boxes defined by the border are perfect rectangles, without any extra bits sticking into the pose box.
    - If the sprite sheet _doesn't_ have a border, that's okay - if all sprites are spaced evenly in a grid, they can still be searched.

2. **Select layers**
    - In Consistxels, navigate to the "Generate Pose Data" menu.
    - Look at the left side of the window. Add your images as layers.
        - Choose name, folder, etc. Some of this info may autofill.
        - Unless you already have a second, updated spritesheet, you can completely ignore the "Source img" part of each layer.
        - Select whether the layer is cosmetic only (in other words, whether you want it to be searched at all.)
        - Select whether to make copies of the _original_ layers to export alongside the individual pose images.
        - Move layers around so they're in the correct order. You can view the preview image to see if it's as you expect.
    - By default, there will already be a "Border" layer. If your sprite sheet doesn't have a border, ignore this for now. If it does, select the border image.

3. **Select search & generation options**
    - Look at the right side of the window.
    - Enter your sprite sheet's name.
    - Select the search type:
        - *Border:* Searches a border image for boxes that contain poses. When selected, a border layer will be automatically created. Add a valid image, with *perfectly rectangular* pose boxes.
        - *Spacing:* Poses are assumed to be spaced out equally from each other.
        - *Preset:* Use a valid .json file that contains pose data (i.e., one generated with the "Generate Pose Data..." button) to search for poses in already-known locations. *(You likely won't have such a file yet. In the next update, you'll be able to create them manually in another menu.)*
    - For your selected search type, fill out the appropriate information. If you select Border, remember that you have to add the image yourself on the left side of the window.
    - Select miscellaneous options:
        - *Start search-in-center:* For each row of the sprite sheet, the middle of the image will be searched, then move rightward until it reaches the edge, at which point it'll return to the center and move leftward.
        - *Search right-to-left:* Reverse the horizontal direction of the search.
        - *Detect identical images:* Pose images that are completely identical to one another will be detected as such.
        - *Detect rotated images:* Pose images that are rotated (in 90-degree intervals only!) will be detected as identical and rotated.
        - *Detect horizontally-mirrored images:* Pose images that are flipped left-to-right, or across the y-axis, or however you wanna say it, will be detected as identical and flipped.
        - *Detect vertically-mirrored images:* Pose images that are flipped top-to-bottom, or across the y-axis, will be detected as identical, rotated, and flipped. (A vertical flip is the same as a horizontal flip plus a 180-degree rotation; due to this redundancy, this feature is disabled if rotation and horizontal flipping are enabled.) **(NOTE TO SELF: SHOULD THIS JUST APPLY TO ROTATION, AND HAVE IT DISABLED IF ROTATION'S ENABLED AT ALL? 'CAUSE, LIKE, AT THAT POINT, JUST USE HORIZONTAL FLIPPING? THINK ABOUT IT)**
    - Here, the "padding" refers to the amount of space between the edge of the actual art, and the edge of the image file. The automatic padding types detect how much space is available, given the restrictions of the pose boxes they're found in. The custom padding adds a flat amount to every edge of every image.

4. **Generate**
    - Select an output folder. (WARNING: You should probably create a new folder to export into! Depending on your sprite sheet, there might be a LOT of pose images, and you don't want to clutter up your files. Additionally, keep in mind that this process WILL overwrite any .json data or pose images from previous generations!!! Sometimes, that's actually want you *want*, though, like if the previous generation went wrong.)
    - Press the "Generate" button to begin generation.
        - This can be cancelled at any time.
        - It will take a noticeable amount of time to complete, but not too long - on my device, when generating data for a sprite sheet with ~650 poses, ~700 pose images, and ~10 layers, generation takes 36 seconds consistently.
        - Generation will almost definitely take longer if you have an older device, but that's a given.
        - You MIGHT notice, like, a 1-second performance dip if you don't keep the window open and in the foreground the entire time. PLEASE tell me if you notice anything more than that, I should be able to do something about it.

**All done!** Now that you have your pose images, you can start editing them.

## Generating updated pose data:

Gonna need to work on this description. In case I don't get to it, it's basically the same process, but you should load a .json file either from a previous generation or from a previous session that was saved manually. From here, you can fiddle with stuff some more if you were dissatisfied with the search method or the padding amount or something.