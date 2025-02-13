from odoo.addons.product_configurator.tests import (
    common as TC,
)


class SaleOrder(TC.ProductConfiguratorTestCases):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.productPricelist = cls.env["product.pricelist"]
        cls.resPartner = cls.env.ref("product_configurator_sale.partenr_sale_1")
        cls.currency_id = cls.env.ref("base.USD")
        cls.ProductConfWizard = cls.env["product.configurator.sale"]

        cls.config_product = cls.env.ref("product_configurator.bmw_2_series")

    def test_00_reconfigure_product(self):
        product_id = self.env["product.product"].create(
            {"product_tmpl_id": self.config_product.id, "name": "Test Product"}
        )
        pricelist_id = self.productPricelist.create(
            {
                "name": "Test Pricelist",
                "currency_id": self.currency_id.id,
            }
        )
        sale_order_id = self.SaleOrder.create(
            {
                "partner_id": self.resPartner.id,
                "partner_invoice_id": self.resPartner.id,
                "partner_shipping_id": self.resPartner.id,
                "pricelist_id": pricelist_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id.id,
                        },
                    )
                ],
            }
        )
        context = dict(
            default_order_id=sale_order_id.id,
            wizard_model="product.configurator.sale",
        )

        self.ProductConfWizard = self.env["product.configurator.sale"].with_context(
            **context
        )
        sale_order_id.action_config_start()
        product_tmpl_id = sale_order_id.order_line.product_id.product_tmpl_id.id
        self.ProductConfWizard.create(
            {"order_id": sale_order_id.id, "product_tmpl_id": product_tmpl_id}
        )
        sale_order_id.order_line.reconfigure_product()
        product_tmpl = sale_order_id.order_line.product_id.product_tmpl_id
        self.assertEqual(
            product_tmpl.id,
            self.config_product.id,
            "Error: If product_tmpl not exsits\
            Method: action_config_start()",
        )
