# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


map_payment_methods = [
    ("payment_method_efectivo", "payment_method_efectivo"),
    ("payment_method_cheque", "payment_method_cheque"),
    ("payment_method_transferencia", "payment_method_transferencia"),
    ("payment_method_tarjeta_de_credito", "payment_method_tarjeta_de_credito"),
    ("payment_method_monedero_electronico", "payment_method_monedero_electronico"),
    ("payment_method_dinero_electronico", "payment_method_dinero_electronico"),
    ("payment_method_vales_despensa", "payment_method_vales_despensa"),
    ("payment_method_12", "payment_method_12"),
    ("payment_method_13", "payment_method_13"),
    ("payment_method_14", "payment_method_14"),
    ("payment_method_15", "payment_method_15"),
    ("payment_method_17", "payment_method_17"),
    ("payment_method_23", "payment_method_23"),
    ("payment_method_24", "payment_method_24"),
    ("payment_method_25", "payment_method_25"),
    ("payment_method_26", "payment_method_26"),
    ("payment_method_27", "payment_method_27"),
    ("payment_method_tarjeta_debito", "payment_method_tarjeta_debito"),
    ("payment_method_tarjeta_servicio", "payment_method_tarjeta_servicio"),
    ("payment_method_30", "payment_method_anticipos"),
    ("payment_method_otros", "payment_method_otros"),
]


def fix_sat_codes(env):
    _logger.warning('Change SAT codes external ids')
    env.cr.execute("""
        UPDATE ir_model_data dest
        SET module = 'product_unspsc', model = 'product.unspsc.code', name = CONCAT('unspsc_code_', SPLIT_PART(src.name, '_', 6))
        FROM ir_model_data src
        WHERE src.id = dest.id AND src.model = 'l10n_mx_edi.product.sat.code';
    """)


def fix_partner_fields(env):
    env.cr.execute("""
        UPDATE res_partner
        SET l10n_mx_edi_locality = l10n_mx_locality
        WHERE l10n_mx_locality IS NOT NULL;
    """)

def remove_l10n_mx_base_data(env):
    env.cr.execute("""
        SELECT id
        FROM ir_model_data
        WHERE module = 'l10n_mx_base' AND model = 'ir.model.access';
    """)
    access_ids = [x[0] for x in env.cr.fetchall()]
    env.cr.execute("""
        DELETE FROM ir_model_access
        WHERE id IN %(ids)s;
    """, {'ids': tuple(access_ids)})
    env.cr.execute("""
        SELECT id
        FROM ir_model_data
        WHERE module = 'l10n_mx_base' AND model = 'res.groups';
    """)
    group_ids = [x[0] for x in env.cr.fetchall()]
    env.cr.execute("""
        DELETE FROM res_groups
        WHERE id IN %(ids)s;
    """, {'ids': tuple(group_ids)})
    env.cr.execute("""
        SELECT id
        FROM ir_act_server
        WHERE name IN ('Ping PAC server', 'Check Account Color Tag')
    """)
    action_server_ids = env.cr.fetchall()
    env.cr.execute("""
        DELETE FROM base_automation WHERE action_server_id IN %(action_server_ids)s;
    """, {
        'action_server_ids': tuple(action_server_ids),
    })
    env.cr.execute("""
        Delete from ir_cron where id in (9, 8)""")
    env.cr.execute("""
        Delete from ir_act_server where id in (365, 631)""")


def fix_payment_method(env):
    env.cr.execute("""
        SELECT
            old.id AS old_id,
            new.id AS new_id 
        FROM l10n_mx_payment_method AS old
        LEFT JOIN l10n_mx_edi_payment_method AS new ON old.code = new.code;
    """)
    res = env.cr.dictfetchall()
    for row in res:        
        env.cr.execute("""
            UPDATE account_move AS am
            SET l10n_mx_edi_payment_method_id = %(new_id)s
            FROM account_invoice AS ai
            WHERE ai.move_id = am.id AND ai.l10n_mx_payment_method_id = %(old_id)s;
        """, row)
        env.cr.execute("""
            UPDATE ir_model_fields SET relation = 'l10n_mx_edi.payment.method'
            WHERE relation = 'l10n_mx.payment.method';
        """)
        # Add a record to avoid no id found error.
        env.cr.execute("""
            INSERT INTO l10n_mx_payment_method(name, code)
            VALUES ('borrar', 'borrar');
        """)
        env.cr.execute("""
            UPDATE res_partner
            SET l10n_mx_payment_method_id = %(new_id)s
            WHERE l10n_mx_payment_method_id = %(old_id)s;
        """, row)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning('Start Migration')
    _logger.warning('Fix locality in partners.')
    fix_partner_fields(env)
    _logger.warning('Remove account types with no internal group')
    env.cr.execute("""
        DELETE FROM account_account_type
        WHERE internal_group IS NULL;
    """)
    _logger.warning('Remove l10n_mx_base data')
    remove_l10n_mx_base_data(env)
    _logger.warning('Fix payment method on invoices.')
    fix_payment_method(env)
