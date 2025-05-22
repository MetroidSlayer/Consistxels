# Consistxels
A tool for more consistent pixel art.
_<sub>If you need to, pronounce it "Consixels" - it's much easier to say. I would've just named it that, but it's less obvious what it's supposed to do that way.</sub>_

**~~Fear~~ _Inconsistency_ is the little-death that brings total obliteration...**

...or, if not obliteration, at least dissatisfaction and subpar sprites.

I hate knowing that one pixel on one pose on a sprite sheet is out-of-place, but I might hate copying and pasting every limb from every layer to double-check even more. The solution was *obviously* to create an entire program to automatically distill a sprite sheet into JSON data, detect identical poses in a given layer, and do all that copying and pasting for me.

Essentially, this program asks you to input the file(s) you wish to get data on, showing which are identical. You can then update a given pose to look a bit different, and then export your sprite sheet. All versions of that pose will now be updated with no extra effort on your part.

This is made to work with multiple layers; i.e., if you have an arm layer and a leg layer, this should be able to update both separately. You'll need to export each layer as its own .png file first when generating the .json, though. Still working out exactly how I want the workflow to go, and still streamlining it.

Hopefully, I get this to work for any given spritesheet, but for now it's just made to work for the Super Metroid Samus sprite sheet used in [SpriteSomething](https://github.com/Artheau/SpriteSomething).