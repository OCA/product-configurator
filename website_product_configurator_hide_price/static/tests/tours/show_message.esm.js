/** @odoo-module **/
import tour from "web_tour.tour";

tour.register(
    "website_product_configurator_hide_price.show_message",
    {
        test: true,
    },
    [
        {
            content: "Check Message is shown",
            trigger: "div[class='alert alert-info'] > span:contains('Price is hidden')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
    ]
);
