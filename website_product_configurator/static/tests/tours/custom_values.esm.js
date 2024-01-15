/** @odoo-module **/
import tour from "web_tour.tour";
import websiteSaleTourUtils from "website_sale.tour_utils";
import websiteTourUtils from "website.tour_utils";

/*
Buy the same product twice with different values for a custom attribute.
Check that two different lines are added in the cart
each showing the chosen custom value
*/
tour.register(
    "website_product_configurator.custom_values",
    {
        test: true,
        url: "/shop",
    },
    [
        {
            content: "Write Glass in search box",
            trigger: "form input[name='search']",
            run: "text Glass",
        },
        websiteTourUtils.clickOnElement(
            "Submit search",
            "form:has(input[name='search']) .oe_search_button"
        ),
        websiteTourUtils.clickOnElement(
            "Select Glass",
            ".oe_product_cart:first a:contains('Glass')"
        ),
        {
            content: "Select Custom value",
            trigger: "#cfg_step_configure",
            run: function () {
                const $options = $("#cfg_step_configure .config_attribute");
                const $custom = $(
                    "#cfg_step_configure .config_attribute option:contains('Custom')"
                );
                $options.val($custom.attr("value")).change();
            },
        },
        {
            content: "Set length 1",
            trigger: "input.custom_config_value",
            run: "text 1",
        },
        websiteTourUtils.clickOnElement(
            "Confirm configuration",
            "button.configureProduct"
        ),
        websiteTourUtils.clickOnElement("Add to cart", "#add_to_cart"),
        websiteSaleTourUtils.goToCart(),
        websiteSaleTourUtils.assertCartContains({
            productName: "Glass",
        }),
        {
            content: "Check that the product has the custom value",
            trigger: ".td-product_name span:contains('Length: 1')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        // Buy another piece of Glass with different length
        websiteTourUtils.clickOnElement("Go to shop", "a[href='/shop']"),
        {
            content: "Write Glass in search box",
            trigger: "form input[name='search']",
            run: "text Glass",
        },
        websiteTourUtils.clickOnElement(
            "Submit search",
            "form:has(input[name='search']) .oe_search_button"
        ),
        websiteTourUtils.clickOnElement(
            "Select Glass",
            ".oe_product_cart:first a:contains('Glass')"
        ),
        {
            content: "Select Custom value",
            trigger: "#cfg_step_configure",
            run: function () {
                const $options = $("#cfg_step_configure .config_attribute");
                const $custom = $(
                    "#cfg_step_configure .config_attribute option:contains('Custom')"
                );
                $options.val($custom.attr("value")).change();
            },
        },
        {
            content: "Set length 2",
            trigger: "input.custom_config_value",
            run: "text 2",
        },
        websiteTourUtils.clickOnElement(
            "Confirm configuration",
            "button.configureProduct"
        ),
        websiteTourUtils.clickOnElement("Add to cart", "#add_to_cart"),
        websiteSaleTourUtils.goToCart({quantity: 2}),
        websiteSaleTourUtils.assertCartContains({
            productName: "Glass",
        }),
        {
            content: "Check that the new product has the new custom value",
            trigger: ".td-product_name span:contains('Length: 2')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content: "Check that the old product has the old custom value",
            trigger: ".td-product_name span:contains('Length: 1')",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
    ]
);
