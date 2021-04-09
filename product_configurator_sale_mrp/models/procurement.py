# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    def _get_matching_bom(self, product_id, values):
        moves = values.get("move_dest_ids")
        bom_id = moves[0].sale_line_id.bom_id if moves else None
        if bom_id:
            values.update(bom_id=bom_id)
        return super(ProcurementRule, self)._get_matching_bom(
            product_id=product_id, values=values
        )
