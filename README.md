# Stickers

## Introduction

`Stickers` is a plugin that allows the artist to add custom decals to any
geometry without worrying about UVs.

Using a custom projection system, the artist is able to move, scale and rotate
any image, making `Stickers` a very flexible system that can be used to create
numerous variants of a character without having to redo its textures every
time or create hundreds of UV sets. All the `Stickers` properties can be animated, 
providing the artist with almost no limitations of what they can do with it. 
Multiple `stickers` can be placed in one geometry which can be useful to creating
more complex rigs like a facial system.

`Stickers` makes combining these 2D and 3D animation techniques a lot easier.

> [!IMPORTANT]
>`Stickers` does not need to modify the UVs of the base surface to work, but 
>it's best to have a regular UV distibution on it.

## Image types

`Stickers` can both load **still images** and **image sequences**. Artist can
then choose between rendering the `sticker` frame by frame, or select
individual frames. This is useful for cases where each image in the sequence is
a different pose or variant of the same element.

> [!WARNING]
>This version of `Stickers` can load only `.png` image type. In next versions 
>we will add more types of images.

## Requirements

* Blender: 4.2

## Install

Download the last version zip file from https://github.com/ANTARUXA/stickers-blender
Put it inside the folder you have chosen, then go to Blender and select in the main 
menu `Edit > Preferences`. 
In the Blender Preferences Panel select the `Add-ons` tab, then select the drop-down 
menu (down arrow) in the upper right corner and press `Install from Disk...`. In the 
File Manager that opens select the zip file you just downloaded and click `Install from Disk` 
and ... that's all.

You could check that the installation has worked if the `Stickers` tab appears in the
3d view sidebar.

## Basic usage

From the 3d view sidebar select the tab `Stickers`, it opens the panel from which we
can get most of the sticker features.

You can move the sticker from the sticker object standard properties, once it has been created. 

Scale and rotation can be done from the custom properties of the sticker object.

The other sticker features such as flip horizontal and vertical, set transparency or 
select the active frame in pose mode, can also be done from the custom properties of the 
sticker object.

### Creating a sticker

To create a `sticker`, open the `Stickers` tab on 3d view sidebar tab. Fill the field 
`Stiker Name` whith the name you have choosen.

> [!IMPORTANT]
> The name of the sticker must be UNIQUE.

Choose an image or the first frame of an image sequence using the folder tool from the
field `Image Filename`. 

> [!IMPORTANT]
> For the sticker to work, an image or sequence of images must always be selected.

Then select the geometry where you want to paste the sticker and switch to `Edit Mode`.
At that time, select only one of the vertices, it is best to select a vertex as close as 
possible to where you want to paste the sticker.

> [!IMPORTANT]
> You must select just ONE vertex.

Press the button `Create Sticker`, and that's all!

Below we see the different types of stickers that we can obtain and how to create each
one of them

#### Base sticker

This is the simplest sticker, just paste a single image on the selected geometry. To create it:

1. Select the image path in the interface as described.

2. Select the desired geometry, change to `Edit Mode` and select jus one vertex.
That vertex will be the starting point for the sticker. The sticker position can be adjusted once
created.

3. After setting everything, click on `Create sticker`.

#### Image Sequence Sticker

With this type of sticker, a sequence of numbered images with an animation will be attached to
the geometry instead of a single image. Animation will play in loop when running the animation
or shuffle over the timeline. To create this kind of sticker:

Check the `Image Sequence` checkbox and follow the same instructions as a
**base sticker**.

#### Multi Pose Sticker

With this sticker we can select which active frame we want within the image sequence we have 
loaded. We will be able to set keys to obtain different poses and create animations that way. 
To create it:

Check the `Multi Pose` checkbox and follow the same instructions as a
**base sticker**.

> [!IMPORTANT]
>For both the `Image Sequence` and `Multi Pose` stickers image files need to be
>numbered. Make sure they follow a pattern that Blender can detect
>as an image sequence

### Shading

Each tag creates a group of nodes connected to the main material of the base geometry. 

The main material is required to be a `Principled BSDRF` shader.
In this version, the sticker nodes are only connected to the `Base Color` input of the main shader.

A texture node connected to the base color input is preferable. If none is connected, the sticker
will automatically create a `Mix` shader node by copying the value of the `Base Color` property
to the `A` input of the new shader mix node. After that, the sticker is connected.

If you later want to change the base color you will have to do it in the `A` entry of the mix node.

The order in which the stickers are projected in the main shader can be changed. A `Stickers` panel
is included in the options sidebar of the `Shader Editor` to do so. You can select the sticker shaders
by sticker name and move it "up" and "down" to avoid (or create) overlappings between different stickers.

Before opening the Shader Editor it is best to have the geometry containing the stickers selected.

### Animation

The `sticker` object is located under the selected geometry. There is a root
node called `{sticker_name}_base_node` that 'anchors' the sticker to the
geometry. The `sticker` is essentially constrained to the surface of the
geometry, and it's movement will depend directly to that.

> [!WARNING]
>`Stickers` will work correctly on animated surfaces with basic transformations
> or shape keys. The sticker will not work well on animated surfaces controlled by armatures
> and bones. We are working on a version called `Rigged Sticker` designed specifically for 
> rigged surfaces.

`{sticker_name}_base_node` which is the main controller node, holds the
principal properties and can be animated.

The `base_node` is in charge of all the channles that can be animated.

1. You need to use standard properties to animate these features:

* Translation

  All 3 axis `X`, `Y`, `Z` are free to move and keyable

2. And custom properties to animate the other sticker features:

* Rotation

  Because the projection is perpendicular to the normal of the geometry, only
  the `Z` axis can be used to rotate the sticker. You'll find a `Rotate` custom
  property in the `base_node` to do that. It's also keyable.

* Scaling

  You can find also in the `base_node` two properties to do scale. Both `ScaleX` and `ScaleY` 
  axis can be scaled and keyed. 

* Flip

  Two custom properties, `flip_X` and `flip_Y`, are meant to mirror the
  sticker horizontally or vertically.

* Transparency

  Using the custom property `transparency` you can control the transparency of the
  sticker (0 - Opaque, 1 - Completely transparent)

* Selecting a specific pose from the frame sequence (only in `Pose Mode`):

  The custom property `active_frame` allows to choose by number one of the poses 
  contained in the sequence of images. Keys can be set for each selected pose.


### Finding the sticker name

For some of `Stickers` utilities you will need to fill in the sticker name in some panels, if
you don't remember it, you can look it up in the custom `sticker_name` property. It is
read-only as the sticker name cannot be changed once it is created.


### Delete a sticker

To delete a given sticker, go to the `Stickers` menu in the 3d view, write the
same unique name of the sticker and press `Remove sticker`.

## Extra functionality

### Move sticker shadernodes up/down in render order

In the sidebar of `Shader Editor` you'll find a `Sticker` tab also that open a
panel from which you can move up and down the sticker shadernodes. Fill the name
of the sticker on `Sticker Name` field and then use the buttons `Move Up` or
`Move Down` to increase or decrease the sticker shadernodes layer position from
top to bottom and vice versa.

### Specific image selection (Multi-pose sticker)

The custom property `active_frame` provides the artist with the ability to select one
image from the *image sequence* and use it as a `pose`, without the image
sequence being linked by the current frame of the scene.

It is possible to consult how many frames are there checking `frame_count` custom
readonly property

By setting this property to any valid number for the image sequence, the
`sticker` will render the selected image.


> [!TIP]
>We recommend to set the animation curves to 'CONSTANT' if you want to avoid
>animation interleaving

## Acknowledgments

We want to thank all the Blender Community for the help we got through different 
tutorials, since this is our first add-on. You have been very helpful. Thank you!

Specially mention to Xinyu Zhu whose great framework https://github.com/xzhuah/BlenderAddonPackageTool
to create, evaluate and release blender add-ons has been fundamental for us.

## TODO:

- [ ] Add support for more texture maps (Normal, Bump, Roughness...)
- [ ] Add better support for more types of image file formats.
- [ ] Add `bake sticker to texture` routine.
- [ ] Add render layer compatibility.
- [ ] `Rigged Stickers` version to manipulate stickers on rigged surfaces.
- [ ] Add a more deep documentation and tutorials.
