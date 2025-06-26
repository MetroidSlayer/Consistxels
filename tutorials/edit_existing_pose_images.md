# Editing existing pose images:

_NOTE: if you **do not yet have pose data**, go to the "Generating pose data" section first._

## Method 1:

This method should be easy-to-understand, but I find it tedious and time-consuming.

1. Open pose images in an external editor and make edits. (Depending on how many pose images there are, opening each individually can be VERY ANNOYING! If you find this tedious, try Method 2 instead. Future versions will have a better workflow.)
2. In the Consistxels main menu, in the "Load & Export Sprite Sheet with Pose Data" section, load a pose data file (in .json format, generated beforehand).
3. Select which layers you want to export, and whether you want them to be merged into a single image, or whether you'd prefer multiple individual layers.
4. Select an output folder and export. Shouldn't take long at all. (Images will be named something like "export_{sprite sheet name}_{layer name, or just "sheet" if it's all merged into one}")

From here, check the exported image, if you want - every single instance of the pose images you modified should be updated across the entire sheet! (If one or more instances *isn't* updated, check your original unmodified pose images and find the offending images - chances are, there are duplicates. This happens when the program does not identify these duplicates as identical during the generation process; this can either be because there were differences in the art that you didn't notice, or because the layers and poses are not separated as effectively as they could be. Either way, it's not a huge deal - you can update the duplicate pose image as well, or make changes to the duplicates to ensure subsequent generations will detect them as identical.)

## Method 2:

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

#
[Back](tutorial_intro.md)