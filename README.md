# Material Bakery
Bake out PBR texture maps in Blender 2.8

Material Bakery executes Cycles baking on the Principled BSDF shader allowing you to flatten your object material stack and export PBR texture maps into other applications.

![example1](https://raw.githubusercontent.com/munro98/MaterialBakery/master/example1.jpg)

Usage
Install addon
Set up a material graph with a single Principled BSDF shader.
Set up a sperate UV texture coordinates used only for baking to.

Once you are done with the material click create maps. 
This will then create several image textures depending on the options chosen in the tick boxes.
The created textures will be postfixed with "_rgh", "_col", ect which is what Material Bakery will try to find(creating duplicate image names breaks things).
A bake node tree will also then be created in each of the materials attached to the object that will be used to bake to.

When Bake is clicked Material Bakery will find the image texture maps inside the created bake node tree and bake to them.


![example2](https://raw.githubusercontent.com/munro98/MaterialBakery/master/example2.jpg)
