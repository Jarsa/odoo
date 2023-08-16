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


def copy_xml_from_payment_to_move(env):
    _logger.warning("Copy xml from payment to move")
    payments = env["account.payment"].search([
        ("state", "=", "posted"),
        ("edi_document_ids", "!=", False),
    ])
    for payment in payments:
        attachments = env["ir.attachment"].search([
            ("res_model", "=", "account.payment"),
            ("res_id", "=", payment.id),
            ("l10n_mx_edi_cfdi_uuid", "!=", False),
        ])
        for attachment in attachments:
            attachment.with_context(states2omit={"draft", "cancel", "posted"}).copy({
                "res_model": "account.move",
                "res_id": payment.move_id.id,
            })


def adapt_edi_format_to_mx(env):
    _logger.warning('Change EDI Format to MX')
    env["account.journal"].search([
        ("edi_format_ids", "!=", False),
    ]).write({
        "edi_format_ids": [(6, 0, env.ref("l10n_mx_edi.edi_cfdi_3_3").ids)],
    })


def fix_taxes_lines(env):
    _logger.warning('Fix taxes lines')
    taxes = env["account.tax"].search([("type_tax_use", "=", "sale")])
    for tax in taxes:
        line = tax.invoice_repartition_line_ids.filtered(lambda x: x.tag_ids)
        other_line = tax.invoice_repartition_line_ids.filtered(lambda x: not x.tag_ids)
        other_line.write({
            "tag_ids": [(6, 0, line.tag_ids.ids)],
        })
        line.write({
            "tag_ids": [(5, 0, 0)],
        })
        line = tax.refund_repartition_line_ids.filtered(lambda x: x.tag_ids)
        other_line = tax.refund_repartition_line_ids.filtered(lambda x: not x.tag_ids)
        other_line.write({
            "tag_ids": [(6, 0, line.tag_ids.ids)],
        })
        line.write({
            "tag_ids": [(5, 0, 0)],
        })


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
    copy_xml_from_payment_to_move(env)
    adapt_edi_format_to_mx(env)
    fix_taxes_lines(env)
    env.cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '15.0.1.4'
        WHERE name = 'base';
    """)
    os.system('say el script de migración ha concluido')
