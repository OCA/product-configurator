/** @odoo-module **/

import {WebsiteSale} from "website_sale.website_sale";

WebsiteSale.include({
    /**
     * Override to inject product assembly
     *
     * @override
     */
    // eslint-disable-next-line no-unused-vars
    _updateRootProduct($form, productId) {
        this._super(...arguments);
        const assembly = $form.find('select[name="assembly"]').val();
        if (assembly) this.rootProduct.assembly = assembly;
    },
});
