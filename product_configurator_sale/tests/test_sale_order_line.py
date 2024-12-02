#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.fields import first
from odoo.tests import Form, new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.configurator_manager_group_xmlid = (
            "product_configurator.group_product_configurator_manager"
        )
        cls.configurator_user_group_xmlid = (
            "product_configurator.group_product_configurator"
        )
        cls.sale_user_group_xmlid = "sales_team.group_sale_salesman"
        cls.configurator_user = new_test_user(
            cls.env,
            login="sale configurator user",
            groups=",".join(
                [
                    cls.configurator_user_group_xmlid,
                    cls.sale_user_group_xmlid,
                ]
            ),
        )

        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
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

        product_template_form = Form(cls.env["product.template"])
        product_template_form.name = "Test configurable template"
        product_template_form.taxes_id.clear()
        with product_template_form.attribute_line_ids.new() as attribute_line:
            attribute_line.attribute_id = cls.attribute
            for value in cls.attribute.value_ids:
                attribute_line.value_ids.add(value)
        product_template = product_template_form.save()
        product_template.config_ok = True
        cls.product_template = product_template

    def _create_wizard(self, sale_order, product_template):
        """Create configuration wizard for `product_template` in `sale_order`."""
        wizard_action = sale_order.action_config_start()
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

    def _configure_product(self, sale_order, product_template, template_values):
        """Configure `product_template` in `sale_order` with values `template_values`."""
        wizard = self._create_wizard(sale_order, product_template)

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
        sale_order = self.sale_order
        self.assertEqual(ptav_10.price_extra, 10)
        self.assertEqual(ptav_20.price_extra, 20)
        self.assertTrue(product_template.config_ok)
        self.assertFalse(sale_order.order_line)

        # Act: Create two order lines, each having a different template attribute value
        self._configure_product(
            sale_order,
            product_template,
            {
                attribute: ptav_10,
            },
        )
        order_line_10 = sale_order.order_line
        self._configure_product(
            sale_order,
            product_template,
            {
                attribute: ptav_20,
            },
        )
        order_line_20 = sale_order.order_line - order_line_10

        # Assert: Each line has the unit price of the configuration session
        config_session_10 = order_line_10.config_session_id
        self.assertEqual(config_session_10.price, order_line_10.price_unit)
        config_session_20 = order_line_20.config_session_id
        self.assertEqual(config_session_20.price, order_line_20.price_unit)
        # Changing the configuration session changes the unit price
        order_line_20.config_session_id = config_session_10
        self.assertEqual(config_session_10.price, order_line_20.price_unit)

    def test_user_access(self):
        """A configurator and sale user
        can configure and add products to sale orders."""
        # Arrange
        configurator_user = self.configurator_user
        product_template = self.product_template
        ptavs = product_template.attribute_line_ids.product_template_value_ids
        ptav_10 = first(ptavs)
        attribute = ptav_10.attribute_id

        with self.with_user(configurator_user.login):
            sale_order = self.env["sale.order"].create(
                {
                    "partner_id": self.customer.id,
                }
            )
            # pre-condition
            self.assertFalse(sale_order.order_line)
            self.assertFalse(
                self.env.user.has_group(self.configurator_manager_group_xmlid)
            )
            self.assertTrue(self.env.user.has_group(self.configurator_user_group_xmlid))
            self.assertTrue(self.env.user.has_group(self.sale_user_group_xmlid))

            # Act
            self._configure_product(
                sale_order,
                product_template,
                {
                    attribute: ptav_10,
                },
            )

        # Assert
        self.assertTrue(sale_order.order_line)

    def test_pricelist_discount_currency(self):
        """
        If the pricelist has a discount,
        the currency of new lines is picked up from the pricelist."""
        # Arrange
        product_template = self.product_template
        ptavs = product_template.attribute_line_ids.product_template_value_ids
        ptav = first(ptavs)
        attribute = ptav.attribute_id

        pricelist = self.env.ref("product.list0")
        pricelist.discount_policy = "without_discount"
        pricelist.item_ids = [
            Command.create(
                {
                    "applied_on": "1_product",
                    "product_tmpl_id": product_template.id,
                }
            )
        ]

        sale_order = self.sale_order
        sale_order.pricelist_id = pricelist
        # pre-condition
        self.assertTrue(pricelist._get_product_rule(product_template, 1))
        self.assertTrue(pricelist.discount_policy, "without_discount")
        self.assertEqual(sale_order.currency_id, pricelist.currency_id)

        # Act
        self._configure_product(
            sale_order,
            product_template,
            {
                attribute: ptav,
            },
        )

        # Assert
        order_line = sale_order.order_line
        self.assertEqual(order_line.currency_id, pricelist.currency_id)
