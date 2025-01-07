# Copyright 2025 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    create_attribute_value = fields.Boolean(
        string="Create attribute value",
        help="When this custom attribute is used, \
        a new value will be generated.",
    )

    @api.constrains(
        "create_attribute_value",
        "val_custom",
    )
    def _constrain_create_attribute_value(self):
        for value in self:
            if value.create_attribute_value and not value.val_custom:
                raise ValidationError(
                    _("'Create attribute value' can only be set on custom values")
                )
