from ..tests.common import (
    TestProductConfiguratorValues,
)


class TestSaleOrder(TestProductConfiguratorValues):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create({"name": "test product"})
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "New Pricelist",
                "currency_id": cls.env.user.company_id.currency_id.id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "name": "test SO",
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": "Test Line",
                            "product_uom_id": cls.product_uom_unit.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 400.00,
                            "config_session_id": cls.session_id.id,
                        },
                    ),
                ],
            }
        )

    def test_cart_update_line_quantity(self):
        """The cart overrides keep the configuration session on the line and
        honour quantity updates (including removal on a zero quantity)."""
        order = self.sale_order.with_context(skip_cart_verification=True)
        order_line = order.order_line
        product_id = order_line.product_id.id

        # The line created in setUpClass carries the configuration session.
        self.assertEqual(order_line.config_session_id, self.session_id)

        # Increasing the quantity preserves the configuration session.
        order._cart_update_line_quantity(line_id=order_line.id, quantity=5)
        self.assertEqual(order_line.product_uom_qty, 5)
        self.assertEqual(order_line.config_session_id, self.session_id)

        # Adding the same product again matches the existing line.
        result = order._cart_add(product_id=product_id, quantity=2)
        self.assertEqual(result.get("line_id"), order_line.id)
        self.assertEqual(order_line.product_uom_qty, 7)

        # Setting the quantity to zero removes the line from the cart.
        order._cart_update_line_quantity(line_id=order_line.id, quantity=0)
        self.assertFalse(order.order_line, "Order line was not removed.")
