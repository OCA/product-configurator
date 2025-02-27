import {ConfigButtonMixin} from "./config_button_mixin.esm.js";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {patch} from "@web/core/utils/patch";

patch(KanbanController.prototype, ConfigButtonMixin(".o-kanban-button-new_config"));
