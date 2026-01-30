/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import { rpc } from "@web/core/network/rpc";

VariantMixin.handleCustomValues = function ($target) {
    console.log('\n\n $target-------------',$target)
    var $variantContainer;
    var $customInput = false;
    if ($target.is('input[type=radio]') && $target.is(':checked')) {
        $variantContainer = $target.closest('ul').closest('li');
        $customInput = $target;
    } else if ($target.is('select')) {
        $variantContainer = $target.closest('li');
        $customInput = $target
            .find('option[value="' + $target.val() + '"]');
    }
    console.log('\n\n $customInput-------------',$customInput)

    if ($variantContainer) {

// Customisation Start
        const $parent = $($target).closest('.js_product');
        console.log('\n\n $parent-------------',$parent)
        var productTemplateId = parseInt($parent.find('.product_template_id').val())
        var attributeId = $variantContainer.data('attribute_id');
        var PTAVId = $customInput.data('value_id');
        const form_data = $parent.find('input, select, textarea').serializeArray();

        rpc("/check/configurator/restriction", {
            'product_template_id': productTemplateId,
            'attribute_id': attributeId,
            'ptav_id': PTAVId,
            'form_data': form_data,
        }).then(function (data) {
            console.log('\n\n data-------------',data)
            if(data && data.is_configured){
                const domainData = data.domain;
                _.each(domainData, function (valueArray, attributeName) {
                    const allOptions = valueArray[0];  // ["White", "Black"]
                    const allowedOptions = valueArray[1];  // ["White"]
                    const operator = valueArray[2]; // e.g. "in"
                    // console.log(`\n\nAttribute: ${attributeName}`);
                    // console.log('All options:', allOptions);
                    // console.log('Allowed options:', allowedOptions);
                    const $selectOptions = $(`option[data-attribute_name="${attributeName}"]`);
                    const $radioOptions = $(`input[data-attribute_name="${attributeName}"]`);
                    const $alloptions = [...$selectOptions, ...$radioOptions];

                if ($alloptions.length) {
                    let activeSelected = false; // check if already have a valid selection

                    $alloptions.forEach(function (opt) {
                        const $opt = $(opt);
                        const valueName = $opt.data('value_name');

                        if (!allowedOptions.includes(valueName)) {
                            // Disable and deselect if this is the selected one
                            $opt.prop('disabled', true);

                            if ($opt.is('option') && $opt.is(':selected')) {
                                $opt.prop('selected', false);
                            }
                            if (($opt.is(':radio') || $opt.is(':checkbox')) && $opt.is(':checked')) {
                                $opt.prop('checked', false);
                            }

                            console.log(`❌ Disabled & Deselected: ${valueName}`);
                        } else {
                            // Enable
                            $opt.prop('disabled', false);

                            // If nothing active is selected yet, choose the first valid one
                            if (!activeSelected) {
                                if ($opt.is('option') && $opt.is(':selected')) {
                                    activeSelected = true; // already selected correctly
                                } else if ($opt.is(':radio') && $opt.is(':checked')) {
                                    activeSelected = true;
                                } else if ($opt.is(':checkbox') && $opt.is(':checked')) {
                                    activeSelected = true;
                                }
                            }
                        }
                    });

                    // If after loop no active option is selected → pick first allowed
                    if (!activeSelected) {
                        const firstAllowed = $alloptions.filter(opt => {
                            return allowedOptions.includes($(opt).data('value_name'));
                        })[0];

                        if (firstAllowed) {
                            const $first = $(firstAllowed);
                            if ($first.is('option')) {
                                $first.prop('selected', true);
                            }
                            if ($first.is(':radio') || $first.is(':checkbox')) {
                                $first.prop('checked', true);
                            }
                            console.log(`⭐ Auto-selected fallback: ${$first.data('value_name')}`);
                        }
                    }
                }

            });                
            }
        });
// Customisation End
            if ($customInput && $customInput.data('is_custom') === 'True') {
                var attributeValueId = $customInput.data('value_id');
                var attributeValueName = $customInput.data('value_name');

                if ($variantContainer.find('.variant_custom_value').length === 0
                        || $variantContainer
                              .find('.variant_custom_value')
                              .data('custom_product_template_attribute_value_id') !== parseInt(attributeValueId)) {
                    $variantContainer.find('.variant_custom_value').remove();

                    const previousCustomValue = $customInput.attr("previous_custom_value");
                    var $input = $('<input>', {
                        type: 'text',
                        'data-custom_product_template_attribute_value_id': attributeValueId,
                        'data-attribute_value_name': attributeValueName,
                        class: 'variant_custom_value form-control mt-2'
                    });

                    $input.attr('placeholder', attributeValueName);
                    $input.addClass('custom_value_radio');
                    $variantContainer.append($input);
                    if (previousCustomValue) {
                        $input.val(previousCustomValue);
                    }
                }
            } else {
                $variantContainer.find('.variant_custom_value').remove();
            }
    }
};
