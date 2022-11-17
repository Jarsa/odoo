# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from datetime import date

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


to_remove = [
    'l10n_mx_edi_vendor_bills',
    'project_timeline_hr_timesheet',
    'web_widget_color',
    'l10n_mx_edi_cancellation_complement',
    'res_currency_rate_custom_decimals',
    'project_task_milestone',
]


# List of strings with XML ID.
records_to_remove = [
]


def change_password(env):
    env.cr.execute("""
        UPDATE res_users
        SET password='admin';
    """)

@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Delete records from XML ID')
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    _logger.warning('Fix tax type.')
    _logger.warning('Define company fields.')
    _logger.warning('Update tax cash basis tax account to reconciled')
    _logger.warning('Uninstalling not required modules')
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
    modules_to_remove.unlink()
    change_password(env)
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
