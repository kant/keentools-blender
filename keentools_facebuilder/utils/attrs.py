# ##### BEGIN GPL LICENSE BLOCK #####
# KeenTools for blender is a blender addon for using KeenTools in Blender.
# Copyright (C) 2019  KeenTools

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####


from .. config import config


# Functions for Custom Attributes perform
def has_custom_attribute(obj, attr_name):
    return attr_name in obj.keys()


def get_custom_attribute(obj, attr_name):
    return obj[attr_name]


def get_safe_custom_attribute(obj, attr_name):
    if has_custom_attribute(obj, attr_name):
        return obj[attr_name]
    else:
        return None


def get_custom_attribute_variants(obj, attr_names):
    for attr in attr_names:
        res = get_safe_custom_attribute(obj, attr)
        if res:
            return res
    return None


def set_custom_attribute(obj, attr_name, val):
    obj[attr_name] = val


def has_keentools_attributes(obj):
    attr_name = config.version_prop_name[0]
    if has_custom_attribute(obj, attr_name):
        return True
    return False


def set_keentools_version(obj, obj_type, ver):
    attr_name = config.version_prop_name[0]
    set_custom_attribute(obj, attr_name, config.addon_version)
    attr_name2 = config.fb_mod_ver_prop_name[0]
    set_custom_attribute(obj, attr_name2, ver)
    attr_name3 = config.object_type_prop_name[0]
    set_custom_attribute(obj, attr_name3, obj_type)


def get_attr_variant_named(data, attr_names):
    for attribute in attr_names:
        if attribute in data.keys():
            return data[attribute]
    return None
