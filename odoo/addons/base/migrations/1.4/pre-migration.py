# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    _logger.warning("Change account type")
    env.cr.execute("update account_account set internal_type='other', internal_group='liability' where code in ('206.01.01','206.01.99');")
    _logger.warning("Delete fiscal positions")
    env.cr.execute("update account_move set fiscal_position_id = null where fiscal_position_id is not null;")
    env.cr.execute("delete from account_fiscal_position;")
    env.cr.execute("delete from ir_property where value_reference like 'account.fiscal.position,';")
    _logger.warning("Set Suspense Account to every company")
    env.cr.execute("""
        update account_journal aj
        set suspense_account_id = ( 
            select id from account_account aa where aa.code='102.01.98' and aa.company_id=aj.company_id ) 
        from ( 
            select id from account_journal aji where aji.type in ('cash','bank') ) as sub
        where aj.id = sub.id;
    """)
