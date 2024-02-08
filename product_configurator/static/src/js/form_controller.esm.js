/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, "Manage special=no_save", {
    async beforeExecuteActionButton(clickParams) {
        if (clickParams.special === "no_save") {
            delete clickParams.special;
            return true;
        }
        return this._super(...arguments);
    },
});
