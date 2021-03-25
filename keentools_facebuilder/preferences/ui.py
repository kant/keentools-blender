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

import sys

from ..preferences.operators import (
    PREF_OT_InstallPkt,
    PREF_OT_InstallFromFilePkt,
    PREF_OT_InstallLicenseOnline,
    PREF_OT_OpenManualInstallPage,
    PREF_OT_CopyHardwareId,
    PREF_OT_InstallLicenseOffline,
    PREF_OT_DownloadsURL,
    PREF_OT_FloatingConnect,
    PREF_OT_OpenPktLicensePage)
from ..blender_independent_packages.pykeentools_loader import (
    module as pkt_module,
    is_installed as pkt_is_installed,
    is_python_supported as pkt_is_python_supported,
    installation_status as pkt_installation_status,
    loaded as pkt_loaded)
from ..config import Config, is_blender_supported
from .formatting import split_by_br_or_newlines
from ..preferences.progress import InstallationProgress
from ..messages import (ERROR_MESSAGES, USER_MESSAGES, draw_system_info,
                        draw_warning_labels, draw_long_labels)


def _multi_line_text_to_output_labels(layout, txt):
    if txt is None:
        return

    all_lines = split_by_br_or_newlines(txt)
    non_empty_lines = filter(len, all_lines)

    col = layout.column()
    col.scale_y = Config.text_scale_y
    for text_line in non_empty_lines:
        col.label(text=text_line)


def _license_was_accepted(prefs):
    return pkt_is_installed() or prefs.license_accepted


def _draw_license_info(prefs, layout):
    layout.label(text='License info:')
    box = layout.box()

    lm = pkt_module().FaceBuilder.license_manager()

    _multi_line_text_to_output_labels(box, lm.license_status_text(force_check=False))

    box.row().prop(prefs, "lic_type", expand=True)

    if prefs.lic_type == 'ONLINE':
        box = layout.box()
        row = box.split(factor=0.85)
        row.prop(prefs, "license_id")
        install_online_op = row.operator(PREF_OT_InstallLicenseOnline.bl_idname)
        install_online_op.license_id = prefs.license_id

    elif prefs.lic_type == 'OFFLINE':
        prefs.hardware_id = lm.hardware_id()

        row = layout.split(factor=0.65)
        row.label(text="Get an activated license file at our site:")
        row.operator(
            PREF_OT_OpenManualInstallPage.bl_idname,
            icon='URL')

        box = layout.box()
        row = box.split(factor=0.85)
        row.prop(prefs, "hardware_id")
        row.operator(PREF_OT_CopyHardwareId.bl_idname)

        row = box.split(factor=0.85)
        row.prop(prefs, "lic_path")
        install_offline_op = row.operator(PREF_OT_InstallLicenseOffline.bl_idname)
        install_offline_op.lic_path = prefs.lic_path

    elif prefs.lic_type == 'FLOATING':
        env = pkt_module().LicenseManager.env_server_info()
        if env is not None:
            prefs.license_server = env[0]
            prefs.license_server_port = env[1]
            prefs.license_server_lock = True
        else:
            prefs.license_server_lock = False

        box = layout.box()
        row = box.split(factor=0.35)
        row.label(text="License Server host/IP")
        if prefs.license_server_lock and prefs.license_server_auto:
            row.label(text=prefs.license_server)
        else:
            row.prop(prefs, "license_server", text="")

        row = box.split(factor=0.35)
        row.label(text="License Server port")
        if prefs.license_server_lock and prefs.license_server_auto:
            row.label(text=str(prefs.license_server_port))
        else:
            row.prop(prefs, "license_server_port", text="")

        if prefs.license_server_lock:
            box.prop(prefs, "license_server_auto",
                     text="Auto server/port settings")

        floating_install_op = row.operator(PREF_OT_FloatingConnect.bl_idname)
        floating_install_op.license_server = prefs.license_server
        floating_install_op.license_server_port = prefs.license_server_port


def _draw_warning_labels(layout, content, alert=True, icon='INFO'):
    col = layout.column()
    col.alert = alert
    col.scale_y = Config.text_scale_y
    for i, c in enumerate(content):
        icon_first = icon if i == 0 else 'BLANK1'
        col.label(text=c, icon=icon_first)
    return col


def _draw_download_install_buttons(prefs, layout):
    # Install online / Install from disk / Download
    row = layout.split(factor=0.35)
    box2 = row.box()
    row2 = box2.row()
    if not prefs.license_accepted:
        row2.active = False
        # row2.alert = True

    op = row2.operator(
        PREF_OT_InstallPkt.bl_idname,
        text='Install online', icon='WORLD')
    op.license_accepted = prefs._license_was_accepted()

    box2 = row.box()
    row2 = box2.split(factor=0.6)
    if not prefs.license_accepted:
        row2.active = False
        # row2.alert = True

    op = row2.operator(
        PREF_OT_InstallFromFilePkt.bl_idname,
        text='Install from disk', icon='FILEBROWSER')
    op.license_accepted = prefs._license_was_accepted()

    op = row2.operator(
        PREF_OT_DownloadsURL.bl_idname,
        text='Download', icon='URL')
    op.url = Config.core_download_website_url


def _draw_please_accept_license(prefs, layout):
    box = layout.box()
    _draw_warning_labels(box, USER_MESSAGES['WE_CANNOT_SHIP'])

    box2 = box.box()
    row = box2.split(factor=0.85)
    row.prop(prefs, 'license_accepted')

    row.operator(
        PREF_OT_OpenPktLicensePage.bl_idname,
        text='Read', icon='URL'
    )

    _draw_download_install_buttons(prefs, box)
    return box


def _draw_download_progress(layout):
    col = layout.column()
    col.scale_y = Config.text_scale_y
    download_state = InstallationProgress.get_state()
    if download_state['active']:
        col.label(text="Downloading: {:.1f}%".format(
            100 * download_state['progress']))
    if download_state['status'] is not None:
        col.label(text="{}".format(download_state['status']))


def _draw_pkt_detail_error_report(layout, status):
    status_to_errors = {
        'NOT_INSTALLED': 'CORE_NOT_INSTALLED',
        'INSTALLED_WRONG': 'INSTALLED_WRONG_INSTEAD_CORE',
        'CANNOT_IMPORT': 'CORE_CANNOT_IMPORT',
        'NO_VERSION': 'CORE_HAS_NO_VERSION',
        'VERSION_PROBLEM': 'CORE_VERSION_PROBLEM',
        'PYKEENTOOLS_OK': 'PYKEENTOOLS_OK'
    }

    assert(status in status_to_errors.keys())
    error = status_to_errors[status]
    assert(error in ERROR_MESSAGES.keys())

    draw_warning_labels(
        layout, ERROR_MESSAGES[error], alert=True, icon='ERROR')

    if status in ('INSTALLED_WRONG', 'CANNOT_IMPORT',
                  'NO_VERSION', 'VERSION_PROBLEM'):
        # Core Uninstall button
        layout.operator(Config.fb_uninstall_core_idname)


def _draw_version(layout):
    arr = ["Version {}, built {}".format(pkt_module().__version__,
                                         pkt_module().build_time),
           'The core library has been installed successfully']
    draw_warning_labels(layout, arr, alert=False, icon='INFO')


def _draw_old_addon(layout):
    box = layout.box()
    draw_warning_labels(box, ERROR_MESSAGES['OLD_ADDON'])
    return box


def _draw_blender_with_unsupported_python(layout):
    box = layout.box()
    draw_warning_labels(
        box, ERROR_MESSAGES['BLENDER_WITH_UNSUPPORTED_PYTHON'])
    return box


def _draw_unsupported_python(layout):
    if is_blender_supported():
        _draw_blender_with_unsupported_python(layout)
    else:
        _draw_old_addon(layout)
        row = layout.split(factor=0.35)
        op = row.operator(
            PREF_OT_DownloadsURL.bl_idname,
            text='Download', icon='URL')
        op.url = Config.core_download_website_url


def _get_problem_info():
    info = []
    if 'pykeentools' in sys.modules:
        try:
            import importlib
            sp = importlib.util.find_spec('pykeentools')
            if sp is not None:
                info.append(sp.origin)
                [info.append(x) for x in sp.submodule_search_locations]
        except Exception:
            info.append('Cannot detect pykeentools spec.')
    else:
        info.append('No pykeentools in modules.')
    return info


def _draw_problem_library(prefs, layout):
    info = _get_problem_info()
    if len(info) == 0:
        return
    layout.prop(prefs, "more_info", toggle=1)
    if not prefs.more_info:
        return
    col = layout.column()
    col.scale_y = Config.text_scale_y
    draw_long_labels(col, info, 120)


def _draw_user_preferences(prefs, layout):
    icon = 'TRIA_RIGHT' if not prefs.show_user_preferences else 'TRIA_DOWN'
    main_box = layout.box()
    if not prefs.show_user_preferences:
        main_box.prop(prefs, 'show_user_preferences', icon=icon)
        return
    main_box.prop(prefs, 'show_user_preferences', icon=icon, invert_checkbox=True)  # emboss=False

    op_name = 'keentools_facebuilder.user_preferences_changer'

    box = main_box.box()
    box.label(text='Pin size and sensitivity')
    row = box.split(factor=0.7)
    row.prop(prefs, 'pin_size', slider=True)
    op = row.operator(op_name, text='Reset')
    op.action = 'revert_default'
    op.param_string = 'pin_size'

    row = box.split(factor=0.7)
    row.prop(prefs, 'pin_sensitivity', slider=True)
    op = row.operator(op_name, text='Reset')
    op.action = 'revert_default'
    op.param_string = 'pin_sensitivity'

    box = main_box.box()
    box.label(text='Default camera focal length')
    row = box.split(factor=0.7)
    row.prop(prefs, 'focal')
    op = row.operator(op_name, text='Reset')
    op.action = 'revert_default'
    op.param_string = 'focal'

    box = main_box.box()
    box.label(text='User Interface')
    row = box.row()
    row.prop(prefs, 'prevent_view_rotation')

    op = main_box.operator(op_name, text='Reset All to Defaults')
    op.action = 'reset_all_to_default'


def draw_preferences_panel(prefs):
    layout = prefs.layout

    if not pkt_is_python_supported():
        _draw_unsupported_python(layout)
        draw_system_info(layout)
        return

    cached_status = pkt_installation_status()
    assert(cached_status is not None)

    if cached_status[1] == 'NOT_INSTALLED':
        if pkt_loaded():
            box = layout.box()
            draw_warning_labels(
                box, USER_MESSAGES['RESTART_BLENDER_TO_UNLOAD_CORE'])
            _draw_problem_library(prefs, box)
            draw_system_info(layout)
            return

        _draw_please_accept_license(prefs, layout)
        _draw_download_progress(layout)
        return

    box = layout.box()
    if cached_status[1] == 'PYKEENTOOLS_OK':
        try:
            _draw_version(box)
            _draw_license_info(prefs, layout)
            _draw_user_preferences(prefs, layout)
            return
        except Exception:
            cached_status[1] = 'NO_VERSION'

    _draw_pkt_detail_error_report(box, cached_status[1])
    _draw_problem_library(prefs, box)
    draw_system_info(layout)

    _draw_download_progress(layout)
