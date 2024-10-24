/** @odoo-module **/

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ProductConfiguratorKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.rpc = useService("rpc");
        this.orm = useService("orm");
    }

    async _onConfigure() {
        const action = await this.orm.call("mrp.production", "action_config_start", []);
        this.action.doAction(action);
    }
}
ProductConfiguratorKanbanController.components = {
    ...KanbanController.components,
};

export const ProductConfiguratorKanbanView = {
    ...kanbanView,
    Controller: ProductConfiguratorKanbanController,
    buttonTemplate: "product_configurator_mrp.KanbanButtons",
};
registry
    .category("views")
    .add("product_configurator_mrp_kanban", ProductConfiguratorKanbanView);
