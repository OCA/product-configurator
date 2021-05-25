odoo.define("website_product_configurator_mrp.config_website_sale_mrp", function (
    require
) {
    "use strict";

    var publicWidget = require("web.public.widget");
    require("website_product_configurator.config_website_sale");

    publicWidget.registry.WebsiteSale.include({
        _onProductReady: function () {
            var $form = this.$form;
            this.rootProduct.assembly = $form.find('select[name="assembly"]').val();
            var res = this._super.apply(this, arguments);
            return res;
        },
    });
});
