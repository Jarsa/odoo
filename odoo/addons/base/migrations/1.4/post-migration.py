# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# List of modules to install
to_install = [
    #'l10n_mx_edi_40',
    #'l10n_mx_edi_extended_40',
    #'l10n_mx_edi_implocal'
    'account_usability',
    'l10n_mx_edi_product_refund_accounts',
]

# List of modules to remove (uninstall)
to_remove = [
    
]

# List of modules to remove all views.
modules_remove_views = [
]

# List of modules to remove all security rules, access and groups.
modules_remove_security = [
]


# List of strings with XML ID.
records_to_remove = [
    'l10n_mx_edi_implocal.l10n_mx_edi_implocal',
    'account_analytic_tag_assign.account_invoice_mtnmx',
    'account_analytic_tag_assign.account_invoice_supplier_mtnmx',
    'account_analytic_tag_assign.purchase_order_mtnmx',
    'account_analytic_tag_assign.purchase_order_mtnmx_analytic_account',
    'account_analytic_tag_assign.sale_order_mtnmx',
]

# List of tuples with the following format
# ('old.model.name', 'new.model.name'),
models_to_rename = [
]

# List of tuples with the following format
# ('old_table_name', 'new_table_name'),
tables_to_rename = [
]

# List of tuples with the following format
# ('model.name', 'table_name', 'old_field', 'new_field'),
fields_to_rename = [
]

# List of tuples with the follwing format
# ('old_module_name', 'new_module_name'),
modules_to_rename = [

]


def rename_modules(env, old, new):
    env['ir.module.module'].update_list()
    _logger.warning(
        'Rename module %s -> %s' % (old, new))
    module = env['ir.module.module'].search(
        [('name', '=', new)])
    old_module = env['ir.module.module'].search(
        [('name', '=', old)])
    module.invalidate_cache()
    if module and old_module:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE name = 'module_%s'" % new)
        env.cr.execute(
            'DELETE FROM ir_module_module WHERE id = %s' % module.id)
        openupgrade.update_module_names(env.cr, [(old, new)])


def remove_module_views(env, module_list):
    def recursive_inherit_ids(records):
        env.cr.execute("""
            SELECT id
            FROM ir_ui_view
            WHERE inherit_id IN %(ids)s;
        """, {'ids': tuple(records.mapped('res_id'))})
        res = env.cr.fetchall()
        view_ids = [x[0] for x in res]
        new_records = env['ir.model.data'].search([
            ('model', '=', 'ir.ui.view'),
            ('res_id', 'in', view_ids)
        ])
        new_records |= records
        if len(new_records) == len(records):
            return records
        return recursive_inherit_ids(new_records)
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.ui.view'),
        ('module', 'in', module_list),
    ])
    records = recursive_inherit_ids(recs)
    return records.mapped('complete_name')


def remove_module_security(env, module_list):
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.model.access'),
        ('module', 'in', module_list),
    ])
    access = env['ir.model.access'].browse(recs.mapped('res_id'))
    access.unlink()
    recs = env['ir.model.data'].search([
        ('model', '=', 'ir.rule'),
        ('module', 'in', module_list),
    ])
    rules = env['ir.rule'].browse(recs.mapped('res_id'))
    rules.unlink()
    recs = env['ir.model.data'].search([
        ('model', '=', 'res.groups'),
        ('module', 'in', module_list),
    ])
    groups = env['res.groups'].browse(recs.mapped('res_id'))
    access = env['ir.model.access'].search([
        ('group_id', 'in', groups.ids)
    ])
    access.unlink()
    groups.unlink()

def remove_views(env):
    env.cr.execute(
            'DELETE FROM ir_ui_view WHERE id IN (2418, 3398, 1507, 3066, 1480, 2778, 2606, 2878, 2443, 1418, 2780, 2607, 2445, 2444, 1449, 1338, 1474, 2779, 2777, 2450, 1501, 1496, 1492, 1490, 1491, 1502, 1479, 1472, 1489, 1580, 3017, 3221, 2541, 2931, 2585, 1385, 1499, 3250, 2613);'
            )

def remove_assets(env):
    env.cr.execute(
        'DELETE FROM  ir_asset WHERE id IN (5, 29, 19, 21, 22)'
    )

@openupgrade.migrate()
def migrate(env, installed_version):
    if records_to_remove:
        _logger.warning('Delete records from XML ID')
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if modules_remove_views:
        _logger.warning('Remove module views')
        openupgrade.delete_records_safely_by_xml_id(
            env, remove_module_views(env, modules_remove_views))
    if modules_remove_security:
        _logger.warning('Remove module security')
        remove_module_security(env, modules_remove_security)
    if modules_to_rename:
        _logger.warning('Modules to rename')
        for module in modules_to_rename:
            rename_modules(env, module[0], module[1])
    if models_to_rename:
        _logger.warning('Models to rename')
        openupgrade.rename_models(env.cr, models_to_rename)
    if tables_to_rename:
        _logger.warning('Tables to rename')
        openupgrade.rename_tables(env.cr, tables_to_rename)
    if fields_to_rename:
        _logger.warning('Fields to rename')
        openupgrade.rename_fields(env, fields_to_rename)
    if to_install:
        env['ir.module.module'].update_list()
        _logger.warning('Installing new modules')
        modules_to_install = env['ir.module.module'].search([
            ('name', 'in', to_install)])
        modules_to_install.button_install()
    if to_remove:
        _logger.warning('Uninstalling not required modules')
        modules_to_remove = env['ir.module.module'].search([
            ('name', 'in', to_remove)])
        modules_to_remove += modules_to_remove.downstream_dependencies()
        modules_to_remove.module_uninstall()
        modules_to_remove.unlink()
    _logger.warning('Delete views')
    remove_views(env)
    remove_assets(env)
