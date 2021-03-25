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

import logging

import bpy
from bpy.app.handlers import persistent

from .settings import get_main_settings


class DefaultUserPreferences:
    pin_size = 7.0
    pin_sensitivity = 16.0
    focal = 50.0
    prevent_view_rotation = True


def _reset_user_preferences_parameter_to_default(param_name):
    settings = get_main_settings()
    prefs = settings.preferences()
    value = getattr(DefaultUserPreferences, param_name)
    setattr(prefs, param_name, value)


def _set_all_user_preferences_to_default():
    all_settings = ['pin_size', 'pin_sensitivity', 'focal',
                    'prevent_view_rotation']
    for name in all_settings:
        _reset_user_preferences_parameter_to_default(name)


class FB_OT_UserPreferencesChanger(bpy.types.Operator):
    bl_idname = 'keentools_facebuilder.user_preferences_changer'
    bl_label = 'FaceBuilder Action'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'FaceBuilder'

    param_string: bpy.props.StringProperty(name='String parameter')
    action: bpy.props.StringProperty(name='Action Name')

    def draw(self, context):
        pass

    def execute(self, context):
        logger = logging.getLogger(__name__)
        logger.debug('user_preferences_changer: {}'.format(self.action))

        if self.action == 'revert_default':
            _reset_user_preferences_parameter_to_default(self.param_string)
            return {'FINISHED'}
        elif self.action == 'reset_all_to_default':
            _set_all_user_preferences_to_default()
            return {'FINISHED'}
        return {'CANCELLED'}


def _copy_user_preferences_parameter_to_settings(param_name):
    settings = get_main_settings()
    prefs = settings.preferences()
    value = getattr(prefs, param_name)
    setattr(settings, param_name, value)


def _copy_user_preferences_to_scene_settings():
    all_settings = ['pin_size', 'pin_sensitivity']
    for name in all_settings:
        _copy_user_preferences_parameter_to_settings(name)


@persistent
def load_handler(*args):
    logger = logging.getLogger(__name__)
    logger.debug('Load Handler call: {}'.format(*args))
    if not FBAddonPreferences.is_addon_loaded():
        remove_load_handler()
        return
    _copy_user_preferences_to_scene_settings()


def remove_load_handler():
    for handler in reversed(bpy.app.handlers.load_post):
        if handler == load_handler:
            bpy.app.handlers.load_post.remove(handler)


def register_load_handler():
    remove_load_handler()
    bpy.app.handlers.load_post.append(load_handler)


def _update_user_preferences_pin_size(self, context):
    settings = get_main_settings()
    prefs = settings.preferences()
    settings.pin_size = self.pin_size

    if prefs.pin_sensitivity < self.pin_size:
        prefs.pin_sensitivity = self.pin_size


def _update_user_preferences_pin_sensitivity(self, context):
    settings = get_main_settings()
    prefs = settings.preferences()
    settings.pin_sensitivity = self.pin_sensitivity

    if prefs.pin_size > self.pin_sensitivity:
        prefs.pin_size = self.pin_sensitivity


class FBAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    _addon_loaded = False

    @classmethod
    def is_addon_loaded(cls):
        return cls._addon_loaded

    @classmethod
    def mark_addon_loaded(cls, status=True):
        register_load_handler()
        cls._addon_loaded = status

    def draw(self, context):
        if self.is_addon_loaded():
            from .preferences.ui import draw_preferences_panel
            draw_preferences_panel(self)

    license_accepted: bpy.props.BoolProperty(
        name='I have read and I agree to KeenTools End-user License Agreement',
        default=False
    )

    license_id: bpy.props.StringProperty(
        name="License ID", default=""
    )

    license_server: bpy.props.StringProperty(
        name="License Server host/IP", default="localhost"
    )

    license_server_port: bpy.props.IntProperty(
        name="License Server port", default=7096, min=0, max=65535
    )

    license_server_lock: bpy.props.BoolProperty(
        name="Variables from ENV", default=False
    )

    license_server_auto: bpy.props.BoolProperty(
        name="Auto settings from Environment", default=True
    )

    hardware_id: bpy.props.StringProperty(
        name="Hardware ID", default=""
    )

    lic_type: bpy.props.EnumProperty(
        name="Type",
        items=(
            ('ONLINE', "Online", "Online license management", 0),
            ('OFFLINE', "Offline", "Offline license management", 1),
            ('FLOATING', "Floating", "Floating license management", 2)),
        default='ONLINE')

    install_type: bpy.props.EnumProperty(
        name="Type",
        items=(
            ('ONLINE', "Online", "Online installation", 0),
            ('OFFLINE', "Offline", "Offline installation", 1)),
        default='ONLINE')

    lic_status: bpy.props.StringProperty(
        name="license status", default=""
    )

    lic_path: bpy.props.StringProperty(
            name="License file path",
            description="absolute path to license file",
            default="",
            subtype="FILE_PATH"
    )

    more_info: bpy.props.BoolProperty(
        name='More Info',
        default=False
    )

    # User preferences
    show_user_preferences: bpy.props.BoolProperty(
        name='Addon User Preferences',
        default=False
    )

    pin_size: bpy.props.FloatProperty(
        description="Set pin size in pixels",
        name="Size",
        default=DefaultUserPreferences.pin_size, min=1.0, max=100.0,
        precision=1,
        update=_update_user_preferences_pin_size)

    pin_sensitivity: bpy.props.FloatProperty(
        description="Set active area in pixels",
        name="Active area",
        default=DefaultUserPreferences.pin_sensitivity,
        precision=1,
        min=1.0, max=100.0, update=_update_user_preferences_pin_sensitivity)

    focal: bpy.props.FloatProperty(
        description="35mm equivalent focal length (mm)",
        name="Focal Length (mm)",
        default=DefaultUserPreferences.focal,
        precision=1,
        min=0.1)

    prevent_view_rotation: bpy.props.BoolProperty(
        name='Prevent view rotation by middle mouse button in pinmode',
        default=DefaultUserPreferences.prevent_view_rotation
    )
