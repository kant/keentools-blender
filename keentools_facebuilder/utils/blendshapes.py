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

import math
import bpy
import numpy as np
import csv


def link_object_to_scene(obj):
    bpy.context.scene.collection.objects.link(obj)


def create_slider_rectangle(name, width=1.0, height=0.2):
    curve = bpy.data.curves.new(name + 'Curve', 'CURVE')
    curve.dimensions = '2D'

    weight = 1
    pline = curve.splines.new('POLY')
    pline.points.add(3)

    pline.points[0].co = (0, -0.5 * height, 0, weight)
    pline.points[1].co = (width, -0.5 * height, 0, weight)
    pline.points[2].co = (width, 0.5 * height, 0, weight)
    pline.points[3].co = (0, 0.5 * height, 0, weight)
    pline.use_cyclic_u = True

    obj = bpy.data.objects.new(name, curve)
    return obj


def create_text_label(name, label='Label', size=0.2):
    text_curve = bpy.data.curves.new(name + 'LabelSpline', type='FONT')
    text_obj = bpy.data.objects.new(name + 'Label', text_curve)
    text_curve.body = label
    text_curve.size = size
    text_obj.hide_select = True
    text_obj.hide_render = True
    link_object_to_scene(text_obj)
    return text_obj


def create_slider(name, label='Label', width=1.0, height=0.2):
    rect = create_slider_rectangle(name + 'Rect', width, height)
    link_object_to_scene(rect)

    em = bpy.data.objects.new(name + 'Empty', None)
    bpy.context.scene.collection.objects.link(em)
    em.empty_display_type = 'CIRCLE'
    em.empty_display_size = 0.35 * height
    em.parent = rect
    em.rotation_euler = (0.5 * math.pi, 0, 0)
    em.location = (0, 0, 0)

    text_obj = create_text_label(name, label, height)
    text_obj.parent = rect
    text_obj.location = (0, 0.6 * height, 0)

    constraint = em.constraints.new('LIMIT_LOCATION')
    constraint.owner_space = 'LOCAL'
    constraint.use_transform_limit = True
    constraint.use_min_x = True
    constraint.use_max_x = True
    constraint.use_min_y = True
    constraint.use_max_y = True
    constraint.use_min_z = True
    constraint.use_max_z = True
    constraint.min_x = 0
    constraint.max_x = 1.0
    constraint.min_y = 0
    constraint.max_y = constraint.min_y
    constraint.min_z = 0
    constraint.max_z = constraint.min_z
    return rect, em


def all_blendshapes_apple():
    return [
        'cheekSquint_R', 'eyeBlink_L', 'mouthSmile_R', 'cheekSquint_L',
        'mouthPucker', 'mouthSmile_L', 'mouthShrugUpper', 'mouthRight',
        'jawLeft', 'browDown_L', 'mouthRollUpper', 'mouthLowerDown_L',
        'eyeWide_R', 'mouthLowerDown_R', 'mouthRollLower', 'jawOpen',
        'mouthUpperUp_L', 'browDown_R', 'eyeLookIn_R', 'browInnerUp',
        'eyeLookUp_L', 'eyeSquint_R', 'mouthFrown_L', 'noseSneer_L',
        'mouthPress_R', 'mouthDimple_R', 'mouthFunnel', 'jawRight',
        'eyeLookDown_R', 'mouthUpperUp_R', 'eyeBlink_R', 'mouthLeft',
        'noseSneer_R', 'mouthClose', 'jawForward', 'eyeLookDown_L',
        'mouthDimple_L', 'eyeLookOut_R', 'tongueOut', 'mouthStretch_R',
        'mouthStretch_L', 'eyeLookOut_L', 'eyeLookIn_L', 'mouthShrugLower',
        'eyeLookUp_R', 'mouthFrown_R', 'browOuterUp_R', 'eyeSquint_L',
        'eyeWide_L', 'cheekPuff', 'browOuterUp_L', 'mouthPress_L']


def all_blendshapes_ue():
    return [
        'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight',
        'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight',
        'eyeWideRight', 'eyeBlinkLeft', 'eyeLookDownLeft',
        'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft',
        'eyeSquintLeft', 'eyeWideLeft', 'jawForward', 'jawRight',
        'jawLeft', 'jawOpen', 'mouthClose', 'mouthFunnel',
        'mouthPucker', 'mouthRight', 'mouthLeft', 'mouthSmileRight',
        'mouthSmileLeft', 'mouthFrownRight', 'mouthFrownLeft',
        'mouthDimpleRight', 'mouthDimpleLeft', 'mouthStretchRight',
        'mouthStretchLeft', 'mouthRollLower', 'mouthRollUpper',
        'mouthShrugLower', 'mouthShrugUpper', 'mouthPressRight',
        'mouthPressLeft', 'mouthLowerDownRight', 'mouthLowerDownLeft',
        'mouthUpperUpRight', 'mouthUpperUpLeft', 'browDownRight',
        'browDownLeft', 'browInnerUp', 'browOuterUpRight',
        'browOuterUpLeft', 'cheekPuff', 'cheekSquintRight',
        'cheekSquintLeft', 'noseSneerRight', 'noseSneerLeft',
        'tongueOut',
        'HeadYaw', 'HeadPitch', 'HeadRoll',
        'LeftEyeYaw', 'LeftEyePitch', 'LeftEyeRoll',
        'RightEyeYaw', 'RightEyePitch', 'RightEyeRoll']


def all_blendshapes_names():
    return all_blendshapes_ue()[:52]


def all_blendshapes_names_sorted():
    arr = all_blendshapes_names()
    arr.sort()
    return arr


def get_all_shape_keys_names(obj):
    res = []
    for kb in obj.data.shape_keys.key_blocks:
        res.append(kb.name)
    return res[1:]


def create_all_blendshapes_sliders(obj):
    width = 1.0
    height = 0.2

    step_x = width * 2
    step_y = height * 2.4
    panel_width = step_x * 4
    panel_height = step_y * 14

    start_x = width * 0.5
    start_y = 0.5 * panel_height - 2 * height


    main_rect = create_slider_rectangle('rig', panel_width, panel_height)
    link_object_to_scene(main_rect)

    blendshapes = get_all_shape_keys_names(obj)
    i = 0
    j = 0
    empties = {}
    for name in blendshapes:
        slider, em = create_slider(name + 'Slider', name, width, height)
        slider.hide_select = True
        empties[name] = em
        slider.parent = main_rect
        slider.location = (start_x + j * step_x, start_y - i * step_y, 0)
        i += 1
        if (i > 12):
            j += 1
            i = 0
    return main_rect, empties


def _move_vertices(shape, vec):
    count = len(shape.data)
    verts = np.empty((count, 3), 'f')
    shape.data.foreach_get('co', np.reshape(verts, count * 3))
    verts += vec
    shape.data.foreach_set('co', verts.ravel())


def create_fake_blendshapes(obj):
    names = all_blendshapes_names()
    obj.shape_key_add(name='Basic')
    for name in names:
        shape = obj.shape_key_add(name=name)
        phi = np.random.uniform(0, np.pi * 2)
        vec = np.array((np.cos(phi), 0, np.sin(phi)))
        _move_vertices(shape, vec)


def create_drivers(obj, empties_dict):
    for kb in obj.data.shape_keys.key_blocks[1:]:
        res = kb.driver_add('value')
        res.driver.type = 'AVERAGE'
        drv_var = res.driver.variables.new()
        drv_var.name = 'DriverName'
        drv_var.type = 'SINGLE_PROP'
        drv_var.targets[0].id = empties_dict[kb.name]
        drv_var.targets[0].data_path = 'location.x'


def read_csv_data(filename):
    results = []
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar=',',
                            quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            results.append(row)
    return results


def parse_row(frame, row, empties_dict):
    timecode = row[0]
    names = all_blendshapes_ue()
    for i, v in enumerate(row[2:54]):
        obj = empties_dict[names[i]]
        obj.location.x = float(v)
        obj.keyframe_insert('location',index=0, frame=frame)


def get_control_empties(obj):
    res = {}
    for d in obj.data.shape_keys.animation_data.drivers:
        blendshape_name = d.data_path.split('"')[1]
        res[blendshape_name] = d.driver.variables[0].targets[0].id
    return res


def load_animation(obj, filepath):
    empties_dict = get_control_empties(obj)
    data = read_csv_data(filepath)
    frame = 1
    for row in data[1:]:
        parse_row(frame, row, empties_dict)
        frame += 1
