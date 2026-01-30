odoo.define("website_product_configurator_restriction.tour_configuration_restriction", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    const tourUtils = require('website_sale.tour_utils');

    tour.register("website_configurator_restriction", {
            test: true,
            url: "/shop",
        },
        [{
                content: "search 2 series",
                trigger: 'form input[name="search"]',
                run: "text 2 series",
            },
            {
                content: "search 2 series",
                trigger: 'form:has(input[name="search"]) .oe_search_button',
            },
            {
                content: "select 2 series",
                trigger: '.oe_product_cart a:contains("2 Series")',
            },
            {
                content: "click to select Fuel",
                trigger: '.js_variant_change[data-value_name="Diesel"]',
            },
            {
                content: "click to select Engine",
                trigger: '.js_variant_change[data-value_name="220d"]',
            },
            {
                content: "click to select Lines",
                trigger: '.js_variant_change[data-value_name="Model Sport Line"]',
            },
            {
                content: "click to select Color",
                trigger: '.js_variant_change[data-value_name="Black"]',
            },
            {
                content: "click to select Rims",
                trigger: '.js_variant_change[data-value_name="V-spoke 18\\""]',
            },
            {
                content: "click to select Tapistry",
                trigger: '.js_variant_change[data-value_name="Oyster/Black"]',
            },
            {
                content: "click to select Transmission",
                trigger: '.js_variant_change[data-value_name="Automatic Sport (Steptronic)"]',
            },
            {
                content: "click to select Options",
                trigger: '.js_variant_change[data-value_name="Armrest"]',
            },
            {
                content: "Click on add to cart",
                trigger: '#add_to_cart',
            },
                tourUtils.goToCart(),
            {
                content: "Proceed to checkout",
                trigger: 'a[href*="/shop/checkout"]',
                run: "click",
            },
        ]
    );
});
