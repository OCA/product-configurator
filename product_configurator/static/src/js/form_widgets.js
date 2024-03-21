odoo.define("product_configurator.FieldBooleanButton", function (require) {
    "use strict";

    var FormController = require("web.FormController");
    var ListController = require("web.ListController");
    var KanbanController = require("web.KanbanController");

    var pyUtils = require("web.py_utils");

    FormController.include({
        /* eslint-disable no-unused-vars*/
        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (
                self.modelName === "product.product" &&
                self.initialState.context.custom_create_variant
            ) {
                this.$buttons.find(".o_form_button_create").css("display", "none");
            }
        },
        /* eslint-disable no-unused-vars*/

        _onButtonClicked: function (event) {
            var self = this;
            var attrs = event.data.attrs;
            if (event.data.attrs.context) {
                var record_ctx = self.model.get(event.data.record.id).context;
                var btn_ctx = pyUtils.eval(
                    "context",
                    record_ctx,
                    event.data.attrs.context
                );
                self.model.localData[event.data.record.id].context = _.extend(
                    {},
                    btn_ctx,
                    record_ctx
                );
            }
            this._super(event);
        },
    });
    ListController.include({
        /* eslint-disable no-unused-vars*/
        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (
                self.modelName === "product.product" &&
                self.initialState.context.custom_create_variant
            ) {
                this.$buttons.find(".o_list_button_add").css("display", "none");
            }
        },
        /* eslint-disable no-unused-vars*/
    });
    KanbanController.include({
        /* eslint-disable no-unused-vars*/
        renderButtons: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (
                self.modelName === "product.product" &&
                self.initialState.context.custom_create_variant
            ) {
                this.$buttons.find(".o-kanban-button-new").css("display", "none");
            }
        },
        /* eslint-disable no-unused-vars*/
    });
});
