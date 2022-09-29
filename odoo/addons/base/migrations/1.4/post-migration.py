# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# List of modules to install
to_install = [
	'l10n_mx_edi_cancellation',
    'l10n_mx_edi_extended',
]

# List of modules to remove (uninstall)
to_remove = [
	'l10n_mx_edi_temp_cancel',
    'pos_reprint',
]

# List of modules to remove all views.
modules_remove_views = [
    'l10n_mx_edi_temp_cancel',
    'pos_reprint',
]

# List of modules to remove all security rules, access and groups.
modules_remove_security = [
]


# List of strings with XML ID.
records_to_remove = [
    'base_user_role.view_res_users_role_form'
]

# List of tuples with the following format
# ('old.model.name', 'new.model.name'),
models_to_rename = [
    #('account.invoice.custom.refund', 'l10n.mx.edi.refund'),
    # ('l10n_mx_edi.product.sat.code', 'product.unspsc.code'),
]

# List of tuples with the following format
# ('old_table_name', 'new_table_name'),
tables_to_rename = [
    # ('l10n_mx_payment_method', 'l10n_mx_edi_payment_method'),
    # ('l10n_mx_edi_product_sat_code', 'product_unspsc_code'),
]

# List of tuples with the following format
# ('model.name', 'table_name', 'old_field', 'new_field'),
fields_to_rename = [
    ('cobertura.zero.analysis', 'cobertura_zero_analysis', 'tipo_persona', 'type_person'),
    ('commission.month_goals', 'commission_month_goals', 'usuario', 'sales_consultant'),
    ('account.move', 'account_move', 'x_real_invoice_date_due', 'credit_days'),
    ('account.move', 'account_move', 'x_invoice_delivered', 'invoice_delivered'),
    ('purchase.order', 'purchase_order', 'x_exchange_rate', 'exchange_rate'),
    ('res.partner', 'res_partner', 'x_phone_two', 'second_phone'),
    ('res.partner', 'res_partner', 'x_mobile_two', 'second_mobile'),
    ('res.partner', 'res_partner', 'x_number_credit_days', 'credit_days'),
    #('res.partner', 'res_partner', 'street2', 'second_street'),
    ('res.partner', 'res_partner', 'x_total_equipo', 'total_equipment'),
    ('res.partner', 'res_partner', 'x_laptops', 'number_laptops'),
    ('res.partner', 'res_partner', 'x_escritorio', 'number_desk'),
    ('res.partner', 'res_partner', 'x_marca_computo', 'computer_brand'),
    ('res.partner', 'res_partner', 'x_impresion', 'impresion'),
    ('res.partner', 'res_partner', 'x_site', 'have_site'),
    ('res.partner', 'res_partner', 'x_servidores', 'servers'),
    ('res.partner', 'res_partner', 'x_marca_site', 'brand_servers'),
    ('res.partner', 'res_partner', 'x_modelo_site', 'server_model'),
    ('res.partner', 'res_partner', 'x_virtuales', 'virtual_servers'),
    ('res.partner', 'res_partner', 'x_hipervisor', 'hipervisor'),
    ('res.partner', 'res_partner', 'x_servicios', 'services'),
    ('res.partner', 'res_partner', 'x_proveedor_internet', 'internet_providers'),
    ('res.partner', 'res_partner', 'x_observaciones', 'additional_remarks'),
    ('res.partner', 'res_partner', 'x_marca_modelo_alm', 'brand_model_storage'),
    ('res.partner', 'res_partner', 'x_cruda', 'raw_capacity'),
    ('res.partner', 'res_partner', 'x_usable', 'usable_capacity'),
    ('res.partner', 'res_partner', 'x_raid', 'raid_disk'),
    ('res.partner', 'res_partner', 'x_switches', 'switches'),
    ('res.partner', 'res_partner', 'x_marca_modelo_switch', 'brand_model_switches'),
    ('res.partner', 'res_partner', 'x_access_point', 'access_point'),
    ('res.partner', 'res_partner', 'x_marca_modelo', 'band_model_access_point'),
    ('res.partner', 'res_partner', 'x_respaldos', 'backups'),
    ('res.partner', 'res_partner', 'x_que_respaldos', 'what_backups'),
    ('res.partner', 'res_partner', 'x_como_respaldos', 'how_to_backup'),
    ('res.partner', 'res_partner', 'x_donde_respaldos', 'where_backup'),
    ('res.partner', 'res_partner', 'x_para_que_respaldos', 'purpose_backups'),
    ('res.partner', 'res_partner', 'x_cuanto_respaldos', 'how_long_backups'),
    ('res.partner', 'res_partner', 'x_firewall', 'firewall'),
    ('res.partner', 'res_partner', 'x_antivirus_serv', 'antivirus_on_server'),
    ('res.partner', 'res_partner', 'x_antivirus', 'antivirus'),
    ('res.partner', 'res_partner', 'x_credit_limit_supplier', 'credit_limit_supplier'),
    ('res.partner', 'res_partner', 'x_credit_used', 'credit_used'),
    ('res.partner', 'res_partner', 'x_credit_available_supplier', 'credit_available_supplier'),
    ('sale.order', 'sale_order', 'tipo_entrega', 'delivery_tipe'),
    ('sale.order', 'sale_order', 'expiration2', 'second_expiration'),
    ('stock.picking', 'stock_picking', 'tipo_entrega', 'delivery_tipe'),
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
            'DELETE FROM ir_ui_view WHERE id IN (160, 2157, 2340, 2339, 2901, 2121, 2341, 2145, 2163);'
        )
def remove_edi_format_id(env):
    env.cr.execute(
            'DELETE FROM account_edi_document WHERE id =13503'
        )


@openupgrade.migrate()
def migrate(env, installed_version):
    if records_to_remove:
        _logger.warning('Delete records from XML ID')
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if modules_remove_views:
        openupgrade.delete_records_safely_by_xml_id(
            env, remove_module_views(env, modules_remove_views))
    if modules_remove_security:
        remove_module_security(env, modules_remove_security)
    if modules_to_rename:
        for module in modules_to_rename:
            rename_modules(env, module[0], module[1])
    if models_to_rename:
        openupgrade.rename_models(env.cr, models_to_rename)
    if tables_to_rename:
        openupgrade.rename_tables(env.cr, tables_to_rename)
    if fields_to_rename:
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
    remove_edi_format_id(env)
