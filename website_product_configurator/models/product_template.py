from odoo import models

from odoo.addons.website.tools import text_from_html


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _to_markup_data(self, website):
        """Generate JSON-LD markup data for the current product template.

        :param website website: The current website.
        :return: The JSON-LD markup data.
        :rtype: dict
        """
        self.ensure_one()

        # When using the configurator (`config_ok`), the template can be shown on the
        # website before any real `product.product` variant exists. In that case,
        # delegating to the variant `_to_markup_data` (as done in the core method)
        # would end up calling `ensure_one()` on an empty recordset and crash.
        #
        # We therefore special‑case templates with no variants: we generate a
        # minimal ProductGroup JSON‑LD directly from the template and avoid
        # touching variants at all.
        if self.config_ok and not self.product_variant_ids:
            base_url = website.get_base_url()
            markup_data = {
                "@context": "https://schema.org/",
                "@type": "ProductGroup",
                "name": self.name,
                "image": f"{base_url}{website.image_url(self, 'image_1920')}",
                "url": f"{base_url}{self.website_url}",
                "hasVariant": [],
            }
            if self.description_ecommerce:
                markup_data["description"] = text_from_html(self.description_ecommerce)
            return markup_data

        return super()._to_markup_data(website)

    def _website_show_quick_add(self):
        """Override to hide quick add button (the cart button on product card at tree
        view) if the template is configured."""
        self.ensure_one()
        if self.config_ok:
            return False
        return super()._website_show_quick_add()
