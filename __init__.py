"""
[Blender and Python] Heavymeta Standard 
Meta-Cronos - August 2022
Email: comicronos@gmail.com
Addon to add standardized meta-data to the scene at the API level.  Standard
Heavmeta Data are offered as a proposed framework that is based on standards
defined here: https://www.nftstandards.wtf/NFT/NFT+Metadata.  Additional att-
ributes have been added to support properties used in 3D art and Animation. 
I have opted to make all NFT related data adsignable at the Collection level.
This seems to make the most sense, given that 3D elements usually a hierarchy
of several object types.
--------
MIT License
Copyright (c) 2022 Heavymeta
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

bl_info = {
    # required
    'name': 'Heavymeta Standard NFT Data',
    'blender': (3, 2, 0),
    'category': 'Collections',
    # optional
    'version': (0, 0, 0),
    'author': 'Meta-Cronos',
    'description': 'Assign Heavymeta Standard properties and meta-data at the Collection level.',
}

import bpy
import re
from rna_prop_ui import PropertyPanel
from bpy.types import (Panel,
                       BoolProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       Collection)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

# -------------------------------------------------------------------
#   Heavymeta Standards Panel
# -------------------------------------------------------------------
PROPS = [
    ('minter_type', bpy.props.EnumProperty(
        name='Minter-Type',
        items=(
            ('HVYC', "Character", ""),
            ('HVYI', "Immortal", ""),
            ('HVYA', "Animal", ""),
            ('HVYW', "Weapon", ""),
            ('HVYO', "Object", ""),
            ('HVYG', "Generic", ""),
            ('HVYAU', "Auricle", "")))),
    ('minter_name', bpy.props.StringProperty(name='Minter-Name', default='')),
    ('minter_description', bpy.props.StringProperty(name='Minter-Description', default='')),
    ('minter_image', bpy.props.StringProperty(name='Minter-Image', subtype='FILE_PATH', default='')),
    ('add_version', bpy.props.BoolProperty(name='Minter-Version', default=False)),
    ('minter_version', bpy.props.IntProperty(name='Version', default=1)),
]


class HVYM_ListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    trait_type: bpy.props.StringProperty(
           name="Type",
           description="meta-data trait type",
           default="")

    type: bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="")

    note: bpy.props.StringProperty(
           name="Note",
           description="Add a note, (not exported).",
           default="")


class HVYM_DataList(UIList):
    """Heavymet data list."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'MEMORY'

        if item.trait_type == 'mesh':
            custom_icon = 'MESH_ICOSPHERE'
        elif item.trait_type == 'morph':
            custom_icon = 'SHAPEKEY_DATA'
        if item.trait_type == 'anim':
            custom_icon = 'ACTION_TWEAK'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.type, icon = custom_icon)
            layout.label(text=item.note)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.type, icon = custom_icon)
            layout.label(text=item.note)

# ------------------------------------------------------------------------
#    Heavymeta Operators
# ------------------------------------------------------------------------
class HVYM_LIST_NewItem(Operator):
    """Add a new item to the list."""

    bl_idname = "hvym_meta_data.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.collection.hvym_meta_data.add()

        return{'FINISHED'}


class HVYM_LIST_NewPropItem(Operator):
    """Add a new nft property item to the list."""

    bl_idname = "hvym_meta_data.new_property_item"
    bl_label = "Add a new property item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'property'

        return{'FINISHED'}

class HVYM_LIST_NewMeshItem(Operator):
    """Add a new mesh item to the list."""

    bl_idname = "hvym_meta_data.new_mesh_item"
    bl_label = "Add a new mesh item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'mesh'

        return{'FINISHED'}

class HVYM_LIST_NewMorphItem(Operator):
    """Add a new morph item to the list."""

    bl_idname = "hvym_meta_data.new_morph_item"
    bl_label = "Add a new morph item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'morph'

        return{'FINISHED'}

class HVYM_LIST_NewAnimItem(Operator):
    """Add a new animation item to the list."""

    bl_idname = "hvym_meta_data.new_anim_item"
    bl_label = "Add a new animation item"

    def execute(self, context):
        item = context.collection.hvym_meta_data.add()
        item.trait_type = 'anim'

        return{'FINISHED'}


class HVYM_LIST_DeleteItem(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "hvym_meta_data.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        hvym_meta_data = context.collection.hvym_meta_data
        index = context.collection.hvym_list_index

        hvym_meta_data.remove(index)
        context.collection.hvym_list_index = min(max(0, index - 1), len(hvym_meta_data) - 1)

        return{'FINISHED'}

class HVYM_LIST_MoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "hvym_meta_data.move_item"
    bl_label = "Move an item in the list"

    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.collection.hvym_list_index
        list_length = len(bpy.context.collection.hvym_meta_data) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.collection.hvym_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        hvym_meta_data = context.collection.hvym_meta_data
        index = context.collection.hvym_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        hvym_meta_data.move(neighbor, index)
        self.move_index(self)

        return{'FINISHED'}

class HVYM_LIST_DirectionUp(bpy.types.Operator):
    """Set direction of HVYM_LIST_MoveItem.deirection to UP."""
    bl_idname = "hvym_meta_data.set_direction_up"
    bl_label = "Set the move direction to up"

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        
        HVYM_LIST_MoveItem.direction = "UP"
        HVYM_LIST_MoveItem.execute(HVYM_LIST_MoveItem, context)
        return{'FINISHED'}


class HVYM_LIST_DirectionDown(bpy.types.Operator):
    """Set direction of HVYM_LIST_MoveItem.deirection to Down."""
    bl_idname = "hvym_meta_data.set_direction_down"
    bl_label = "Set the move direction to down"

    @classmethod
    def poll(cls, context):
        return context.collection.hvym_meta_data

    def execute(self, context):
        
        HVYM_LIST_MoveItem.direction = "DOWN"
        HVYM_LIST_MoveItem.execute(HVYM_LIST_MoveItem, context)
        return{'FINISHED'}


class HVYM_DataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Heavymeta Standard"
    bl_idname = "COLLECTION_PT_heavymeta_standard_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        col = self.layout.column()
        ctx = context.collection
        for (prop_name, _) in PROPS:
            row = col.row()
            if prop_name == 'minter_version':
                row = row.row()
                row.enabled = context.collection.add_version
            row.prop(context.collection, prop_name)
        row = col.row()
        row.separator()
        row.label(text="Traits:")
        row = col.row()
        row.template_list("HVYM_DataList", "The_List", ctx,
                          "hvym_meta_data", ctx, "hvym_list_index")

        row = col.row()
        row.operator('hvym_meta_data.new_property_item', text='+', icon='MEMORY')
        row.operator('hvym_meta_data.new_mesh_item', text='+', icon='MESH_ICOSPHERE')
        row.operator('hvym_meta_data.new_morph_item', text='+', icon='SHAPEKEY_DATA')
        row.operator('hvym_meta_data.new_anim_item', text='+', icon='ACTION_TWEAK')
        row.operator('hvym_meta_data.delete_item', text='', icon='CANCEL')
        row.operator('hvym_meta_data.set_direction_up', text='', icon='SORT_DESC')
        row.operator('hvym_meta_data.set_direction_down', text='', icon='SORT_ASC')

        if ctx.hvym_list_index >= 0 and ctx.hvym_meta_data:
            item = ctx.hvym_meta_data[ctx.hvym_list_index]

            row = col.row()
            row.prop(item, "type")
            row.prop(item, "note")


# -------------------------------------------------------------------
#   Class Registration
# -------------------------------------------------------------------
blender_classes = [
    HVYM_ListItem,
    HVYM_DataList,
    HVYM_LIST_NewItem,
    HVYM_LIST_NewPropItem,
    HVYM_LIST_NewMeshItem,
    HVYM_LIST_NewMorphItem,
    HVYM_LIST_NewAnimItem,
    HVYM_LIST_DeleteItem,
    HVYM_LIST_MoveItem,
    HVYM_LIST_DirectionUp,
    HVYM_LIST_DirectionDown,
    HVYM_DataPanel
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Collection, prop_name, prop_value)

    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    bpy.types.Collection.hvym_meta_data = bpy.props.CollectionProperty(type = HVYM_ListItem)
    bpy.types.Collection.hvym_list_index = bpy.props.IntProperty(name = "Index for hvym_meta_data",
                                             default = 0)


def unregister():
    del bpy.types.Collection.hvym_meta_data
    del bpy.types.Collection.hvym_list_index

    for (prop_name, _) in PROPS:
        delattr(bpy.types.Collection, prop_name)

    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

if __name__ == "__main__":
    register()