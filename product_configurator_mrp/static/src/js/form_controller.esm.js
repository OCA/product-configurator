import {ConfigButtonMixin} from "./config_button_mixin.esm.js";
import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, ConfigButtonMixin(".o_form_button_create_config"));
