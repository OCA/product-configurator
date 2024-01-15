from ..tests.test_website_product_configurator_values import (
    TestProductConfiguratorValues,
)


class TestSaleOrder(TestProductConfiguratorValues):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env["product.product"].create({"name": "test product"})
        self.product_uom_unit = self.env.ref("uom.product_uom_unit")
        self.pricelist = self.env.ref("product.list0")
        self.sale_order = self.env["sale.order"].create(
            {
                "name": "test SO",
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": "Test Line",
                            "product_uom": self.product_uom_unit.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 400.00,
                            "config_session_id": self.session_id.id,
                        },
                    ),
                ],
            }
        )

    def test_cart_update(self):
        product_id = (
            self.sale_order.order_line.product_id.product_tmpl_id.product_variant_id.id
        )
        self.sale_order._cart_update(
            product_id=product_id,
            line_id=self.sale_order.order_line.id,
            set_qty=0,
            add_qty=0,
        )
        self.assertFalse(
            self.product.product_tmpl_id.config_ok, "product is config_ok True"
        )
        self.product.product_tmpl_id.write({"config_ok": True})
        cart_update = self.sale_order._cart_update(
            product_id=product_id,
            line_id=self.sale_order.order_line.id,
            set_qty=2,
            add_qty=2,
        )
        self.assertEqual(cart_update.get("line_id"), self.sale_order.order_line.id)
        self.assertEqual(
            cart_update.get("quantity"), self.sale_order.order_line.product_uom_qty
        )

        self.sale_order.write({"order_line": False})
        self.sale_order._cart_update(
            product_id=product_id,
            set_qty=1,
            add_qty=1,
        )
        self.assertTrue(self.sale_order.order_line, "No Sale Order Line created.")

        self.sale_order._cart_update(
            product_id=product_id,
            line_id=self.sale_order.order_line.id,
            set_qty=-1,
            add_qty=1,
        )
        self.assertFalse(
            self.sale_order.order_line,
            "Order Line is exist for quantity is less than equal zero.",
        )

        self.sale_order._cart_update(
            line_id=self.sale_order.order_line.id,
            product_id=product_id,
            add_qty="test",
        )
        self.assertEqual(
            self.sale_order.order_line.product_uom_qty,
            1,
            "If wrong value is added then 1 quantity is deducted from Order Line.",
        )

        self.sale_order._cart_update(
            line_id=self.sale_order.order_line.id,
            product_id=product_id,
            set_qty="test",
        )
        self.assertEqual(
            self.sale_order.order_line.product_uom_qty,
            1,
            "If wrong value is added then Order Line quantity as it is.",
        )

    def test_cart_update_multi_attribute(self):
        """A product having multiple values selected for a multi attribute
        can be added to cart"""
        # Arrange
        session = self.session_id
        session.value_ids |= (
            self.env.ref("product_configurator.product_attribute_value_218i")
            | self.env.ref("product_configurator.product_attribute_value_rims_378")
            | self.env.ref(
                "product_configurator.product_attribute_value_tapistry_black"
            )
            | self.env.ref("product_configurator.product_attribute_value_sport_line")
            | self.env.ref("product_configurator.product_attribute_value_armrest")
            | self.env.ref(
                "product_configurator.product_attribute_value_smoker_package"
            )
        )
        session.action_confirm()
        product = session.product_id
        # pre-condition: Product has multiple values for a multi attribute
        multi_attribute_line = self.env.ref(
            "product_configurator.product_attribute_line_2_series_options"
        )
        self.assertTrue(multi_attribute_line.multi)
        multi_attribute = multi_attribute_line.attribute_id
        multi_values = product.product_template_attribute_value_ids.filtered(
            lambda ptav, attribute=multi_attribute: ptav.attribute_id == multi_attribute
        )
        self.assertGreater(len(multi_values), 1)

        # Act
        result = self.sale_order._cart_update(
            product.id,
            add_qty=1,
        )

        # Assert
        order_line = self.env["sale.order.line"].browse(result["line_id"])
        self.assertEqual(order_line.product_id, product)
