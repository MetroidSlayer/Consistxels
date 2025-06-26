# Generating new sprite sheet data:

_NOTE: if you **already have sprite sheet data**, you can [skip this section completely](edit_existing_pose_images.md)! This only matters if you want to make edits to a fully- or mostly-completed sprite sheet that does not yet have sprite sheet data._

1. **Format your sprite sheet**
    - Go through your sprite sheet, ensuring that every pose is separate, and every limb (or whatever your character has) is actually identical to every other limb like it. Even the smallest, most minute differences will cause the program to identify them as completely different pose images. If possible, remove such differences; if doing so would change the art in any meaningful way, and you want to avoid doing that, you'll just have to deal with needing to edit multiple similar-looking pose images later.
    - Export each layer as its own image file.
    - If the sprites are separated by a border, make sure that border is a SINGLE color, without any variation. Also, **make sure** pose boxes defined by the border are perfect rectangles, without any extra bits sticking into the pose box.
    - If the sprite sheet _doesn't_ have a border, that's okay - if all sprites are spaced evenly in a grid, they can still be searched.

2. **Select layers**
    - In Consistxels, navigate to the "Generate Sprite Sheet Data" menu.
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
        - *Preset:* Use a valid .json file that contains pose locations (i.e., one generated with the "Generate Sheet Data..." button) to search for poses in already-known locations. *(You likely won't have such a file yet. In the next update, you'll be able to create them manually in another menu.)*
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

**All done!** Now that you have your pose images, you can [start editing them](edit_existing_pose_images.md).

#
[Back](tutorial_intro.md)