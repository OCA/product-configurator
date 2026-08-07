import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";

patch(WebsiteSale.prototype, {
    /**
     * Update the root product during an Add process.
     *
     * @override
     * @param {HTMLFormElement} form - The form in which the product is.
     */
    _updateRootProduct(form) {
        // Call the original method to keep existing functionality
        super._updateRootProduct(...arguments);

        // Extend the rootProduct to include the `config_session_id`
        const configSessionInput = form.querySelector(
            'input[name="config_session_id"]'
        );
        if (configSessionInput) {
            this.rootProduct.config_session_id = configSessionInput.value;
        }
    },
});
