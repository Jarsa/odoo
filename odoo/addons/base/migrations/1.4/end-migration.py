# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

from datetime import date

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


to_remove = [
    'web_widget_many2many_tags_multi_selection',
    'siti_custom_css',
    'stock_kardex',
    'account_reconciliation_uuid',
]


# List of strings with XML ID.
records_to_remove = []


def fix_l10n_mx_cfdi_tax_type(env):
    values_to_fix = {
        'rate': 'Tasa',
        'quota': 'Couta',
        'exempt': 'Exento',
    }
    for old_value, new_value in values_to_fix.items():
        env.cr.execute("""
            UPDATE account_tax
            SET l10n_mx_tax_type = '%s'
            WHERE l10n_mx_tax_type = '%s'
        """ % (new_value, old_value))


def define_compay_fields(env):
    env.cr.execute("""
        UPDATE res_company
        SET
        account_cash_basis_base_account_id = 454,
        l10n_mx_edi_pac = 'finkok',
        l10n_mx_edi_pac_username = 'sitibt@odoo.com',
        l10n_mx_edi_pac_password = '16e4add63257a90965d62212782913488d4a2196d119fd92a637faa39db2',
        l10n_mx_edi_fiscal_regime = '601'
    """)


def process_tax_accounts(env):
    """ Tax accounts must have reconcile = True when tax cash basis is
    configured and you use multi currency
    """
    taxes = env['account.tax'].search([('tax_exigibility', '=', 'on_payment')])
    accounts = taxes.mapped('cash_basis_transition_account_id')
    accounts.write({
        'reconcile': True,
    })


def process_invoices(env):
    invoices = env['account.move'].search([
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
    ])
    count = 1
    for invoice in invoices:
        _logger.warning('Processing invoice %s of %s' % (count, len(invoices)))
        count += 1
        attachment = env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', invoice.id),
            ('name', '=ilike', '%.xml'),
        ], limit=1)
        if not attachment:
            continue
        env['account.edi.document'].create({
            'move_id': invoice.id,
            'edi_format_id': env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'attachment_id': attachment.id,
            'state': 'sent',
        })
    payments = env['account.payment'].search([
        ('state', '=', 'posted'),
        ('payment_type', '=', 'inbound'),
    ])
    count = 1
    for payment in payments:
        _logger.warning('Processing payment %s of %s' % (count, len(payments)))
        count += 1
        attachment = env['ir.attachment'].search([
            ('res_model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('name', '=ilike', '%.xml'),
        ], limit=1)
        if not attachment:
            continue
        env['account.edi.document'].create({
            'move_id': payment.move_id.id,
            'edi_format_id': env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
            'attachment_id': attachment.id,
            'state': 'sent',
        })


def add_certificate(env):
    companies = env['res.company'].search([])
    for company in companies:
        env.cr.execute("""
            SELECT
                file_cer AS content,
                file_key AS key,
                password AS password,
                serial_number AS serial_number,
                date_start AS date_start,
                date_end AS date_end
            FROM res_certificate
            WHERE company_id = %(company_id)s
        """, {'company_id': company.id})
        certificates = env.cr.dictfetchall()
        for certificate in certificates:
            if certificate.get('date_end') < date.today():
                continue
            certificate = env['l10n_mx_edi.certificate'].create(certificate)
            company.write({
                'l10n_mx_edi_certificate_ids': [(4, certificate.id)],
            })


def sitibt_routes(env):
    env['stock.location'].create({
        'name': 'Consignaciones',
        'usage': 'internal',
    })
    route = env['stock.location.route'].browse(8)
    consignment_location = env['stock.location'].search(
        [('name', '=', 'Consignaciones')])
    route.ensure_one()
    route.write({
        'rule_ids': [
            (5, 0, 0),
            (0, 0, {
                'name': 'Entrega consignación',
                'action': 'pull',
                'picking_type_id': 1,
                'location_src_id': consignment_location.id,
                'location_id': 9,
                'procure_method': 'make_to_order',
                'sequence': 20,
                'group_propagation_option': 'propagate',
            }),
            (0, 0, {
                'name': 'Salida de consignación',
                'action': 'pull',
                'picking_type_id': 3,
                'location_src_id': 16,
                'location_id': consignment_location.id,
                'procure_method': 'make_to_order',
                'sequence': 21,
                'group_propagation_option': 'propagate',
            }),
        ],
    })


def users_res_groups(env):
    env['res.groups'].create({
        'name': 'Usuario (solo vista)',
        'category_id': 201,
        'users': [
            (4, 2),
            (4, 16),
            (4, 8),
            (4, 9),
            (4, 12),
            (4, 14),
        ],
        'view_access': [
            #(4, 2748),
            (4, 2778),
            #(4, 2296),
            (4, 796),
            (4, 595),
            (4, 802),
            #(4, 1962)
        ],
        'menu_access': [
            (4, 250),
        ],
        'implied_ids': [
            (4, 1),
        ],
    },
    )
    env['res.groups'].create({
        'name': 'Creacion de contactos (solo vista)',
        'category_id': 57,
        'users': [
            (4, 2),
            (4, 16),
            (4, 14),
        ],
        'menu_access': [
            (4, 306),
        ],
    },
    )
    env['res.groups'].create({
        'name': 'Usuario (solo vista)',
        'category_id': 193,
        'users': [
            (4, 2),
            (4, 26),
            (4, 16),
            (4, 9),
        ],
        'menu_access': [
            (4, 223),
            (4, 645),
            (4, 200),
            (4, 271),
        ],
        'view_access': [
            (4, 718),
            (4, 719),
        ],
        'implied_ids': [
            (4, 93),
            (4, 1),
        ],
    },
    )
    env['res.groups'].create({
        'name': 'Usuario (solo vista)',
        'category_id': 190,
        'users': [
            (4, 2),
            (4, 22),
            (4, 26),
            (4, 16),
            (4, 28),
        ],
        'menu_access': [
            (4, 275),
        ],
        'implied_ids': [
            (4, 93),
            (4, 38),
            (4, 1),
        ],
        'view_access': [
            (4, 2800),
            (4, 2801),
            (4, 933),
            (4, 917),
            (4, 916),
        ],
    },
    )
    env['res.groups'].create({
        'name': 'Usuario (solo vista)',
        'category_id': 192,
        'users': [
            (4, 2),
            (4, 22),
            (4, 26),
            (4, 9),
        ],
        'menu_access': [
            (4, 365),
            (4, 364),
        ],
        'view_access': [
            (4, 1047),
            (4, 3732),
            (4, 3731),
        ],
        'implied_ids': [
            (4, 1),
        ],
    },
    )
    env['res.groups'].create({
        'name': 'Usuario: Solo mostrar documentos propios (solo vista)',
        'category_id': 191,
        'users': [
            (4, 2),
            (4, 22),
            (4, 26),
            (4, 16),
            (4, 8),
            (4, 9),
            (4, 11),
            (4, 12),
            (4, 14),
        ],
        'menu_access': [
            (4, 198),
            (4, 194),
            (4, 674),
            (4, 195),
            (4, 675),
            (4, 181),
            (4, 845),
            (4, 851),
            (4, 269),
        ],
        'view_access': [
            (4, 608),
            (4, 3867),
            (4, 3879),
            (4, 3866),
            (4, 594),
            (4, 595),
            (4, 3371),
            (4, 2408),
            (4, 3864),
            (4, 607),
        ],
        'implied_ids': [
            (4, 1),
        ],
    },
    )
    env['res.groups'].create({
        'name': 'Usuario: Todos los documentos (solo vista)',
        'category_id': 191,
        'users': [
            (4, 2),
            (4, 22),
            (4, 26),
            (4, 16),
            (4, 14),
        ],
        'rule_groups': [
            (0, 0, {
                'name': 'All Orders Lines',
                'model_id': 285,
                'domain_force': [(1, '=', 1)],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Orders Analysis',
                'model_id': 287,
                'domain_force': [(1, '=', 1)],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Invoices Analysis',
                'model_id': 236,
                'domain_force': [(1, '=', 1)],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Invoice Send and Print',
                'model_id': 557,
                'domain_force': [('invoice_ids.move_type', 'in', ('out_invoice', 'out_refund'))],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Invoices Lines',
                'model_id': 201,
                'domain_force': [('move_id.move_type', 'in', ('out_invoice', 'out_refund'))],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Invoice Lines',
                'model_id': 201,
                'domain_force': [('move_id.move_type', 'in', ('out_invoice', 'out_refund'))],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Orders',
                'model_id': 284,
                'domain_force': [(1, '=', 1)],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Salesteam',
                'model_id': 174,
                'domain_force': [(1, '=', 1)],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Invoices',
                'model_id': 200,
                'domain_force': [('move_type', 'in', ('out_invoice', 'out_refund'))],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
            (0, 0, {
                'name': 'All Invoices',
                'model_id': 200,
                'domain_force': [('move_type', 'in', ('out_invoice', 'out_refund'))],
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            }),
        ],
    },
    )


def remove_assets(env, to_remove):
    for module in to_remove:
        env['ir.asset'].search([('path', 'like', module)]).unlink()
    env['ir.asset'].search(
        [('path', 'like', 'stock_interface_kiosk')]).unlink()


def remove_stock_rule_Wo_location_id(env):
    env['stock.rule'].browse(49).unlink()


def activate_views(env):
    env.cr.execute("""
        UPDATE ir_ui_view
        SET active = 'true'
        WHERE model_data_id = '176561'
        OR model_data_id = '119539' 
        OR model_data_id = '224627';;
    """)


def add_currency_precision_for_mx(env):
    env.cr.execute("""
        UPDATE res_currency
        SET l10n_mx_edi_decimal_places = 2;
    """)


def change_password(env):
    env.cr.execute("""
        UPDATE res_users
        SET password='admin';
    """)


def fix_constraint(env):
    env.cr.execute("""
        UPDATE account_move_line
        SET amount_currency = (credit*-1)
        WHERE (
                (
                    (currency_id != company_currency_id)
                    AND
                    (
                        (debit - credit <= 0 AND amount_currency <= 0)
                        OR
                        (debit - credit >= 0 AND amount_currency >= 0)
                    )
                )
                OR
                (
                    currency_id = company_currency_id
                    AND
                    ROUND(debit - credit - amount_currency, 2) = 0
                )
            ) = false AND debit = '0';

        UPDATE public.account_move_line
        SET amount_currency = debit
        WHERE (
                (
                    (currency_id != company_currency_id)
                    AND
                    (
                        (debit - credit <= 0 AND amount_currency <= 0)
                        OR
                        (debit - credit >= 0 AND amount_currency >= 0)
                    )
                )
                OR
                (
                    currency_id = company_currency_id
                    AND
                    ROUND(debit - credit - amount_currency, 2) = 0
                )
            ) = false AND credit = '0';
    """)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Delete records from XML ID')
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    _logger.warning('Fix tax type.')
    fix_l10n_mx_cfdi_tax_type(env)
    _logger.warning('Define company fields.')
    define_compay_fields(env)
    _logger.warning('Add certificate to companies.')
    add_certificate(env)
    _logger.warning('Update tax cash basis tax account to reconciled')
    process_tax_accounts(env)
    _logger.warning('Reset base module to version 1.3')
    process_invoices(env)
    _logger.warning('Uninstalling not required modules')
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
    modules_to_remove.unlink()
    remove_assets(env, to_remove)
    activate_views(env)
    users_res_groups(env)
    sitibt_routes(env)
    remove_stock_rule_Wo_location_id(env)
    change_password(env)
    fix_constraint(env)
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
