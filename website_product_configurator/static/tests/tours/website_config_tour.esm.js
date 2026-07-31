import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("config", {
    url: "/shop",
    sequence: 20,

    steps: () => [
        {
            content: "search 2 series",
            trigger: 'form input[name="search"]',
            run: "edit 2 series",
        },
        {
            content: "search 2 series",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "select 2 series",
            trigger: '.oe_product_cart a:contains("2 Series")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "click to select fuel",
            trigger: ".tab-pane.fade.container.show.active select",
            run: "selectByLabel Gasoline",
        },
        {
            content: "click to select engine",
            trigger:
                '.tab-pane.fade.container.show.active select.form-control.config_attribute.cfg-select.required_config_attrib:has(option:contains("218i"))',
            run: "selectByLabel 218i",
        },
        {
            content: "click on continue",
            trigger: "span:contains(Continue)",
            run: "click",
        },
        {
            content: "click to select color",
            trigger: ".tab-pane.fade.container.show.active select",
            run: "selectByLabel Silver",
        },
        {
            content: "click to select rims",
            trigger:
                '.tab-pane.fade.container.show.active select.form-control.config_attribute.cfg-select.required_config_attrib:has(option:contains("V-spoke 16"))',
            run: "selectByLabel V-spoke 16",
        },
        {
            content: "wait for the Lines configuration step",
            trigger: ".nav-item.config_step a:contains(Lines)",
        },
        {
            content: "click on continue",
            trigger: "span:contains(Continue)",
            run: "click",
        },
        {
            content: "click to select Lines",
            trigger: ".tab-pane.fade.container.show.active select",
            run: "selectByLabel Sport Line",
        },
        {
            content: "click on continue",
            trigger: "span:contains(Continue)",
            run: "click",
        },
        {
            content: "click to select tapistry",
            trigger: ".tab-pane.fade.container.show.active select",
            run: "selectByLabel Black",
        },
        {
            content: "click on continue",
            trigger: "span:contains(Continue)",
            run: "click",
        },
        {
            content: "click to select Transmission",
            trigger: ".tab-pane.fade.container.show.active select",
            run: "selectByLabel Automatic",
        },
        {
            content: "click to select Options",
            trigger:
                '.tab-pane.fade.container.show.active select.form-control.config_attribute.cfg-select.required_config_attrib:has(option:contains("Armrest"))',
            run: "selectByLabel Armrest",
        },
        {
            // This final "Continue" completes the configuration. The
            // configurator then submits it (save_configuration with
            // submit_configuration=true), creates the product variant and
            // redirects to the configured product page via window.location.
            //
            // That redirect runs asynchronously, from the save_configuration
            // RPC promise callback, so it fires a beforeunload roughly 100ms
            // after this click. It MUST be the last step and carry
            // expectUnloadPage: true: that keeps the tour engine's allowUnload
            // flag true (no later step resets it) so the async unload is
            // accepted, then the tour resumes on the configured product page
            // and completes.
            content: "click on continue to finish the configuration",
            trigger: "span:contains(Continue)",
            run: "click",
            expectUnloadPage: true,
        },
    ],
});
