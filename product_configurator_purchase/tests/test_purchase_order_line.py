#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.customer.id,
            }
        )

        attribute_form = Form(cls.env["product.attribute"])
        attribute_form.name = "Test attribute"
        with attribute_form.value_ids.new() as value:
            value.name = "Test value 1"
        with attribute_form.value_ids.new() as value:
            value.name = "Test value 2"
        cls.attribute = attribute_form.save()
        cls.product_template = cls.env.ref("product_configurator.bmw_2_series")

    def _create_wizard(self, purchase_order, product_template):
        """Create configuration wizard for `product_template` in `purchase_order`."""
        wizard_action = purchase_order.action_config_start()
        wizard_model = self.env[wizard_action["res_model"]]
        wizard_context = wizard_action.get("context", {})
        wizard = wizard_model.with_context(**wizard_context).create(
            {
                "product_tmpl_id": product_template.id,
            }
        )
        return wizard

    def _configure_wizard(self, wizard, template_values):
        """Fill `wizard` with `template_values`."""
        # Fill in the values
        fields_prefixes = wizard._prefixes
        field_prefix = fields_prefixes.get("field_prefix")
        for attribute, ptav in template_values.items():
            dynamic_attribute_name = field_prefix + str(attribute.id)
            wizard.write(
                {
                    dynamic_attribute_name: ptav.product_attribute_value_id.id,
                }
            )
        return wizard.action_config_done()

    def _configure_product(self, purchase_order, product_template, template_values):
        """
        Configure `product_template` in `purchase_order` with values `template_values`.
        """
        wizard = self._create_wizard(purchase_order, product_template)

        return self._configure_wizard(wizard, template_values)

    def test_config_session_change_price_unit(self):
        """
        The unit price is the price of the configuration session.
        """
        # Arrange: create a product with 2 product template attribute values
        # having extra price 10 and 20 respectively
        product_template = self.product_template
        ptavs = product_template.attribute_line_ids.product_template_value_ids
        ptav_10 = first(ptavs)
        ptav_10.price_extra = 10
        ptav_20 = first(ptavs - ptav_10)
        ptav_20.price_extra = 20
        attribute = ptav_10.attribute_id
        purchase_order = self.purchase_order
        self.assertEqual(ptav_10.price_extra, 10)
        self.assertEqual(ptav_20.price_extra, 20)
        self.assertTrue(product_template.config_ok)
        self.assertFalse(purchase_order.order_line)

        # Act: Create two order lines, each having a different template attribute value
        self._configure_product(
            purchase_order,
            product_template,
            {
                attribute: ptav_10,
            },
        )
        order_line_10 = purchase_order.order_line
        self._configure_product(
            purchase_order,
            product_template,
            {
                attribute: ptav_20,
            },
        )
        order_line_20 = purchase_order.order_line - order_line_10

        # Assert: Each line has the unit price of the configuration session
        config_session_10 = order_line_10.config_session_id
        self.assertEqual(config_session_10.price, order_line_10.price_unit)
        config_session_20 = order_line_20.config_session_id
        self.assertEqual(config_session_20.price, order_line_20.price_unit)
        # Changing the configuration session changes the unit price
        order_line_20.config_session_id = config_session_10
        self.assertEqual(config_session_10.price, order_line_20.price_unit)
