#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_variant_for_combination(self, combination):
        self.ensure_one()
        if self.config_ok and combination:
            variant = self.env["product.config.session"].search_variant(
                product_tmpl_id=self,
                value_ids=combination.product_attribute_value_id.ids,
            )
        else:
            variant = super()._get_variant_for_combination(
                combination,
            )
        return variant

    def _get_possible_combinations(
        self, parent_combination=None, necessary_values=None
    ):
        self.ensure_one()
        if not self.config_ok:
            yield from super()._get_possible_combinations(
                parent_combination=parent_combination,
                necessary_values=necessary_values,
            )
        else:
            # For configurable products,
            # custom values cannot be found among ptavs
            # because it is actually a flag in the pta.
            # super() would get stuck trying any possible combination
            # for filling the missing ptav.
            yield necessary_values or self.env[
                "product.template.attribute.value"
            ].browse()

    def _is_combination_possible_by_config(self, combination, ignore_no_variant=False):
        self.ensure_one()
        if not self.config_ok:
            res = super()._is_combination_possible_by_config(
                combination,
                ignore_no_variant=ignore_no_variant,
            )
        else:
            try:
                self.env["product.config.session"].validate_configuration(
                    value_ids=combination.product_attribute_value_id.ids,
                    product_tmpl_id=self.id,
                )
            except ValidationError:
                res = False
            else:
                res = True
        return res
