const {document} = globalThis;
import {onMounted} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export function ConfigButtonMixin(buttonSelector) {
    return {
        setup() {
            super.setup?.(...arguments);
            this.orm = useService("orm");
            this.actionService = useService("action");

            onMounted(() => {
                const rootEl = this.el || document;
                const button = rootEl.querySelector(buttonSelector);
                if (button && this.props?.resModel === "mrp.production") {
                    button.style.display = "block";
                    button.addEventListener("click", () => this._onConfigure());
                }
            });
        },

        async _onConfigure() {
            const action = await this.orm.call(
                "mrp.production",
                "action_config_start",
                [],
                {}
            );
            if (action) {
                this.actionService.doAction(action);
            }
        },
    };
}
