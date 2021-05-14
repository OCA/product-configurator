odoo.define("website_product_configurator.config_website_sale", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    publicWidget.registry.WebsiteSale.include({
        /**
         * Initializes the optional products modal
         * and add handlers to the modal events (confirm, back, ...)
         *
         * @private
         * @param {$.Element} $form the related webshop form
         * @returns {Object}
         * Override method to add config session
         */
        _handleAdd: function ($form) {
            var self = this;
            this.$form = $form;

            var productSelector = [
                'input[type="hidden"][name="product_id"]',
                'input[type="radio"][name="product_id"]:checked',
            ];

            var productReady = this.selectOrCreateProduct(
                $form,
                parseInt($form.find(productSelector.join(", ")).first().val(), 10),
                $form.find(".product_template_id").val(),
                false
            );
            return productReady.then(function (productId) {
                $form.find(productSelector.join(", ")).val(productId);

                self.rootProduct = {
                    product_id: productId,
                    quantity: parseFloat(
                        $form.find('input[name="add_qty"]').val() || 1
                    ),
                    product_custom_attribute_values: self.getCustomVariantValues(
                        $form.find(".js_product")
                    ),
                    variant_values: self.getSelectedVariantValues(
                        $form.find(".js_product")
                    ),
                    no_variant_attribute_values: self.getNoVariantAttributeValues(
                        $form.find(".js_product")
                    ),
                    config_session_id: $form
                        .find('input[name="config_session_id"]')
                        .val(),
                };
                return self._onProductReady();
            });
        },
    });
});
