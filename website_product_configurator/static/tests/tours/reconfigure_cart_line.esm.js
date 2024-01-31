/** @odoo-module **/
import tour from "web_tour.tour";

import websiteSaleTourUtils from "website_sale.tour_utils";

tour.register(
    "website_product_configurator.reconfigure_cart_line",
    {
        test: true,
    },
    [
        {
            content: "Add to cart",
            trigger: "#add_to_cart",
        },
        websiteSaleTourUtils.goToCart({quantity: 1}),
        {
            content: "Check Silver car is in cart",
            trigger: "#cart_products td.td-product_name strong:contains('Silver')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content: "Click on reconfigure link",
            trigger: "td[class='td-reconfigure_action'] > a",
        },
        {
            content: "Check banner is shown",
            trigger: "div[role='alert']",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content: "Go to Body step",
            trigger: "#product_config_form a:contains('Body')",
            run: "click",
        },
        {
            content: "Select Red color",
            // Paint color is the first select of the active tab
            trigger: "div.show[role='tabpanel'] select",
            run: function () {
                const color_select = $("div.show[role='tabpanel'] select")[0];
                const $red = $(color_select).find("option:contains('Red')");
                $(color_select).val($red.attr("value")).change();
            },
        },
        {
            content: "Go to last step",
            trigger: "#product_config_form a:contains('Extras')",
        },
        {
            content: "Confirm",
            trigger: "button#form_action span:contains('Continue')",
        },
        {
            content: "Check configured car is red",
            trigger: "#product_details span:contains('Red')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content: "Add to cart",
            trigger: "#add_to_cart",
        },
        {
            content: "Check banner is shown",
            trigger: "div[role='alert']",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        websiteSaleTourUtils.goToCart({quantity: 1}),
        {
            content: "Check Red car is in cart",
            trigger: "#cart_products td.td-product_name strong:contains('Red')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
    ]
);
