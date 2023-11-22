/** @odoo-module **/
const {onMounted, onRendered, useRef, useState} = owl;
import {BooleanField} from "@web/views/fields/boolean/boolean_field";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class BooleanButtonField extends BooleanField {
    setup() {
        super.setup();
        this.state1 = useState({value: 0});
        this.root = useRef("root");
        onMounted(() => {
            this.updateConfigurableButton();
        });
        onRendered(() => {
            this.updateConfigurableButton();
        });
    }

    onChange() {
        this.state1.value++;
    }

    updateConfigurableButton() {
        this.text = this.props.value
            ? this.props.activeString
            : this.props.inactiveString;
        this.hover = this.props.value
            ? this.props.inactiveString
            : this.props.activeString;
        var val_color = this.props.value ? "text-success" : "text-danger";
        var hover_color = this.props.value ? "text-danger" : "text-success";
        var $val = $("<span>")
            .addClass("o_stat_text o_boolean_button o_not_hover " + val_color)
            .text(this.text);
        var $hover = $("<span>")
            .addClass("o_stat_text o_boolean_button o_hover d-none " + hover_color)
            .text(this.hover);
        $(this.root.el).empty();
        $(this.root.el).append($val).append($hover);
    }
}

BooleanButtonField.props = {
    ...standardFieldProps,
    activeString: {type: String, optional: true},
    inactiveString: {type: String, optional: true},
};

BooleanButtonField.extractProps = ({attrs}) => {
    return {
        activeString: attrs.options.active,
        inactiveString: attrs.options.inactive,
    };
};

BooleanButtonField.template = "product_configurator.BooleanButtonField";
registry.category("fields").add("boolean_button", BooleanButtonField);
