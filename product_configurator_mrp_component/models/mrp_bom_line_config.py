# Copyright (C) 2022-Today Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MRPBoMLineConfig(models.Model):
    _name = "mrp.bom.line.config"
    _description = "BOM Line Configuration"

    def _get_default_product_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order="id").id

    bom_id = fields.Many2one(
        "mrp.bom",
        string="BoM",
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Configurable Product",
        required=True,
    )
    product_qty = fields.Float(
        "Quantity",
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        default=_get_default_product_uom_id,
        string="Product Unit of Measure",
        required=True,
    )
    available_config_components = fields.Many2many(
        "product.template",
        related="bom_id.available_config_components",
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        domain = args or []
        domain += ["|", ("name", operator, name), ("default_code", operator, name)]
        return self.search(domain, limit=limit).name_get()
