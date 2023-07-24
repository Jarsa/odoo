# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


to_remove = [
]


# List of strings with XML ID.
records_to_remove = [
]


@openupgrade.migrate()
def migrate(env, installed_version):
    if records_to_remove:
        _logger.warning('Delete records from XML ID')
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if to_remove:
        _logger.warning('Uninstalling not required modules')
        modules_to_remove = env['ir.module.module'].search([
            ('name', 'in', to_remove)])
        modules_to_remove += modules_to_remove.downstream_dependencies()
        modules_to_remove.module_uninstall()
        modules_to_remove.unlink()
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
