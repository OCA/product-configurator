/** @odoo-module **/
import tour from "web_tour.tour";

tour.register(
    "website_product_configurator_hide_price.show_price",
    {
        test: true,
    },
    [
        {
            content: "Check Price is shown",
            trigger: ".js_main_product .oe_price",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
    ]
);
