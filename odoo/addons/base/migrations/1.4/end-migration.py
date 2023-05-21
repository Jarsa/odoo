# Copyright 2022 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from datetime import date

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


to_remove = [
    'account_coa_menu',
    'account_fiscalyear_close_analytic', #validar  https://github.com/Jarsa/account-fix-tools
    'account_fiscalyear_close', #validar  https://github.com/Jarsa/account-fix-tools
    'account_group_menu',
    'account_invoice_currency_date_invoice',
    'account_invoice_fix_number',#-------------------
    'account_invoice_tier_validation',
    'account_menu',
    'account_refund_change_account',
    'account_tag_menu', #validar
    'account_type_menu',
    'bi_sql_editor_aggregate',
    'hr_contract_document', #validar
    'hr_contract_reference',
    'hr_employee_document',#validar
    'l10n_mx_edi_addendas',
    'l10n_mx_edi_bank',
    'l10n_mx_edi_cancellation_complement',
    'l10n_mx_edi_vendor_bills',
    'l10n_mx_edi_vendor_validation',
    'project_recalculate',
    'project_stage_closed',
    'project_task_dependency',
    'project_task_milestone',
    'project_template_milestone',
    'project_timeline_hr_timesheet', #validar
    'project_timeline_task_dependency',
    'proyecto_recalcular',
    'res_currency_rate_custom_decimals',
    'web_widget_color',
]


# List of strings with XML ID.
records_to_remove = [
]


def change_password(env):
    env.cr.execute("""
        UPDATE res_users
        SET password='admin';
    """)

def fix_tier_definition(env):
    _logger.warning("Adapt tier definition from account.invoice to account.move")
    env.cr.execute("""
        UPDATE tier_definition
        SET model='account.move'
        WHERE model='account.invoice';
    """)
    definitions = env["tier.definition"].search([('model', '=', 'account.move')])
    for definition in definitions:
        definition.write({
            "definition_domain": definition.definition_domain.replace(
                '"account_analytic_id"', '"analytic_account_id.name"').replace(
                '"type"', '"move_type"')
        })

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
    _logger.warning('Update account move set analytic account')
    env.cr.execute("""
        UPDATE account_move am
        SET analytic_account_id = (
            SELECT ai.account_analytic_id
            FROM account_invoice ai
            WHERE ai.move_id = am.id
        );
    """)
    _logger.warning('Update account move set analytic tag')
    env.cr.execute("""
        UPDATE account_move am
        SET account_analytic_tag_id = (
            SELECT ai.account_analytic_tag_id
            FROM account_invoice ai
            WHERE ai.move_id = am.id
        );
    """)
    _logger.warning('Update account move set team analytic account')
    env.cr.execute("""
        UPDATE account_move am
        SET team_account_analytic_tag_id = (
            SELECT ai.team_account_analytic_tag_id
            FROM account_invoice ai
            WHERE ai.move_id = am.id
        );
    """)
    _logger.warning("Activate views")
    env.cr.execute("update ir_ui_view set active=true where id in (1466,1453,2611,1467,2707);")
    fix_tier_definition(env)
    _logger.warning("Restore module base to version 1.4")
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
