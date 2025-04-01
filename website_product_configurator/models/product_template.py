from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _is_combination_possible(
        self, combination, parent_combination=None, ignore_no_variant=False
    ):
        """Inherited the method to enhance combination validation for configurable
        products (config_ok) and ensured the 'Add to Cart' button functions correctly
        after selecting multiple options."""

        self.ensure_one()
        # Check if the default method restricts the combination, but the product is
        # configurable.
        if (
            not self._is_combination_possible_by_config(combination, ignore_no_variant)
            and self.config_ok
        ):
            return True

        return super()._is_combination_possible(
            combination,
            parent_combination=parent_combination,
            ignore_no_variant=ignore_no_variant,
        )
