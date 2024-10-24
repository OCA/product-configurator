from odoo.addons.product_configurator.tests.common import ProductConfiguratorTestCases


class SaleOrder(ProductConfiguratorTestCases):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.productPricelist = cls.env["product.pricelist"]
        cls.partner = cls.env.ref("product_configurator_sale.partenr_sale_1")
        cls.currency = cls.env.ref("base.USD")
        cls.ProductConfWizard = cls.env["product.configurator.sale"]

    def test_00_reconfigure_product(self):
        pricelist_id = self.productPricelist.create(
            {
                "name": "Test Pricelist",
                "currency_id": self.currency.id,
            }
        )
        sale_order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "pricelist_id": pricelist_id.id,
            }
        )
        context = dict(
            default_order_id=sale_order.id,
            wizard_model="product.configurator.sale",
        )

        self.ProductConfWizard = self.env["product.configurator.sale"].with_context(
            **context
        )
        sale_order.action_config_start()
        self._configure_product_nxt_step(order_id=sale_order.id)
        sale_order.order_line.reconfigure_product()
        product_tmpl = sale_order.order_line.product_id.product_tmpl_id
        self.assertEqual(
            product_tmpl.id,
            self.config_product.id,
            "Error: If product_tmpl not exsits\
            Method: action_config_start()",
        )
