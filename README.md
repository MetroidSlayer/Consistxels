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
- All generated poses and images have automatically-generated names, and at the moment, renaming any of these will usually break things. Next update will feature a way to rename poses and images, as well as add layers and poses manually post-generation. This should ease clarity when either opening images for editing or sharing generated data with others.
- Not every sprite sheet has even spacing or a perfect border. Next update will feature a way to select poses on a sprite sheet manually, allowing images to be searched no matter how they're formatted. Support for irregularly-sized pose boxes during border searches will also happen at some point.

If you notice any bugs, feel free to open an issue or reach out to me on [Discord](https://discord.com/users/mattroid9313). Same goes for requesting new features; if you think something might be helpful, I'd love to hear it.

## Tutorials
Tutorials can be found [here](tutorials/tutorial_intro.md).