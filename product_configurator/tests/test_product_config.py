from odoo.exceptions import UserError, ValidationError

from ..tests.common import ProductConfiguratorTestCases

# FIXME: many tests here do not have any assertions.
# They simply run something and expect it to not raise an exception.
# This is not a good practice. Tests should have assertions.


class ProductConfig(ProductConfiguratorTestCases):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.productConfWizard = cls.env["product.configurator"]
        cls.productTemplate = cls.env["product.template"]
        cls.productAttribute = cls.env["product.attribute"]
        cls.productAttributeVals = cls.env["product.attribute.value"]
        cls.productAttributeLine = cls.env["product.template.attribute.line"]
        cls.productConfigSession = cls.env["product.config.session"]
        cls.productConfigDomain = cls.env["product.config.domain"]
        cls.config_product = cls.env.ref("product_configurator.bmw_2_series")
        cls.attr_engine = cls.env.ref("product_configurator.product_attribute_engine")
        cls.config_step_engine = cls.env.ref("product_configurator.config_step_engine")
        cls.config_product_1 = cls.env.ref(
            "product_configurator.product_config_line_gasoline_engines"
        )
        cls.config_product_2 = cls.env.ref(
            "product_configurator.2_series_config_step_body"
        )
        # domain
        cls.domain_gasolin = cls.env.ref(
            "product_configurator.product_config_domain_gasoline"
        )
        cls.domain_engine = cls.env.ref(
            "product_configurator.product_config_domain_diesel"
        )
        cls.config_image_red = cls.env.ref("product_configurator.config_image_1")
        # value
        cls.value_gasoline = cls.env.ref(
            "product_configurator.product_attribute_value_gasoline"
        )
        cls.value_diesel = cls.env.ref(
            "product_configurator.product_attribute_value_diesel"
        )
        cls.value_red = cls.env.ref("product_configurator.product_attribute_value_red")
        # config_step
        cls.config_step_engine = cls.env.ref("product_configurator.config_step_engine")
        cls.attribute_line = cls.env.ref(
            "product_configurator.product_attribute_line_2_series_engine"
        )
        cls.value_silver = cls.env.ref(
            "product_configurator.product_attribute_value_silver"
        )
        cls.value_rims_387 = cls.env.ref(
            "product_configurator.product_attribute_value_rims_387"
        )
        # attribute line
        cls.attribute_line_2_series_rims = cls.env.ref(
            "product_configurator.product_attribute_line_2_series_rims"
        )
        cls.attribute_line_2_series_tapistry = cls.env.ref(
            "product_configurator.product_attribute_line_2_series_tapistry"
        )
        cls.attribute_value_tapistry_oyster_black = cls.env.ref(
            "product_configurator." + "product_attribute_value_tapistry_oyster_black"
        )
        cls.attribute_line_2_series_transmission = cls.env.ref(
            "product_configurator.product_attribute_line_2_series_transmission"
        )

        # attribute value
        cls.attribute_rims = cls.env.ref("product_configurator.product_attribute_rims")
        cls.attribute_tapistry = cls.env.ref(
            "product_configurator.product_attribute_tapistry"
        )
        cls.attribute_transmission = cls.env.ref(
            "product_configurator.product_attribute_transmission"
        )

        # session id
        cls.session_id = cls.productConfigSession.create(
            {
                "product_tmpl_id": cls.config_product.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.value_gasoline.id,
                            cls.value_transmission.id,
                            cls.value_red.id,
                        ],
                    )
                ],
                "user_id": cls.env.user.id,
            }
        )
        # ir attachment
        cls.irAttachement = cls.env["ir.attachment"].create(
            {
                "name": "Test attachement",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
            }
        )

        # configure product
        cls._configure_product_nxt_step()
        cls.config_session = cls.productConfigSession.search(
            [("product_tmpl_id", "=", cls.config_product.id)]
        )

        # create product template
        cls.product_tmpl_id = cls.productTemplate.create({"name": "Coca-Cola"})
        # create attribute 1
        cls.attribute_1 = cls.productAttribute.create(
            {
                "name": "Color",
            }
        )
        # create attribute 2
        cls.attribute_2 = cls.productAttribute.create(
            {
                "name": "Flavour",
            }
        )

        # create attribute value 1
        cls.attribute_vals_1 = cls.productAttributeVals.create(
            {
                "name": "Orange",
                "attribute_id": cls.attribute_1.id,
            }
        )
        # create attribute value 2
        cls.attribute_vals_2 = cls.productAttributeVals.create(
            {
                "name": "Balck",
                "attribute_id": cls.attribute_1.id,
            }
        )
        # create attribute value 3
        cls.attribute_vals_3 = cls.productAttributeVals.create(
            {
                "name": "Coke",
                "attribute_id": cls.attribute_2.id,
            }
        )
        # create attribute value 4
        cls.attribute_vals_4 = cls.productAttributeVals.create(
            {
                "name": "Mango",
                "attribute_id": cls.attribute_2.id,
            }
        )

    # TODO :: Left to take review of code
    def test_00_check_value_attributes(self):
        with self.assertRaises(ValidationError):
            self.config_product_1.write(
                {"value_ids": [(6, 0, [self.value_gasoline.id])]}
            )

    def test_01_check_config_step(self):
        with self.assertRaises(ValidationError):
            self.config_product_2.config_step_id = 4

    def test_02_get_trans_implied(self):
        self.domain_gasolin.write({"implied_ids": [(6, 0, [self.domain_engine.id])]})
        trans_implied_ids = self.domain_gasolin.trans_implied_ids.ids
        self.assertEqual(
            trans_implied_ids[-1],
            self.domain_engine.id,
            "Error: If value not exists\
            Method: _get_trans_implied()",
        )

    def test_03_check_config_step(self):
        with self.assertRaises(ValidationError):
            self.env["product.config.step.line"].create(
                {
                    "product_tmpl_id": self.config_product.id,
                    "config_step_id": self.config_step_engine.id,
                    "attribute_line_ids": [(6, 0, [self.attribute_line.id])],
                }
            )

    def test_04_compute_cfg_price(self):
        # check for _compute_cfg_price
        price = self.config_product.list_price
        price += self.value_220i.product_id.lst_price
        price += self.value_model_sport_line.product_id.lst_price
        price += self.value_transmission.product_id.lst_price
        price += self.value_options_2.product_id.lst_price
        self.assertEqual(
            self.session_id.price,
            price,
            "Error: If different session price and list_price\
            Method: _compute_cfg_price",
        )

    def test_05_get_custom_vals_dict(self):
        # check for _get_custom_vals_dict
        productConfigSessionCustVals = self.env[
            "product.config.session.custom.value"
        ].create(
            {"cfg_session_id": self.session_id.id, "attribute_id": self.attr_fuel.id}
        )
        # check for custom type Int
        self.attr_fuel.custom_type = "integer"
        productConfigSessionCustVals.update({"value": 154})
        checkIntval = self.session_id._get_custom_vals_dict()
        attr_id = productConfigSessionCustVals.attribute_id.id
        self.assertEqual(
            checkIntval.get(attr_id),
            154,
            "Error: If Not Integer value or False\
            Method: _get_custom_vals_dict()",
        )
        # check for custom type Float
        self.attr_fuel.custom_type = "float"
        productConfigSessionCustVals.update({"value": 94.5})
        checkFloatval = self.session_id._get_custom_vals_dict()
        attr_id = productConfigSessionCustVals.attribute_id.id
        self.assertEqual(
            checkFloatval.get(attr_id),
            94.5,
            "Error: If Not Float value or False\
            Method: _get_custom_vals_dict()",
        )
        # check for custom type Binary
        self.attr_color.custom_type = "binary"
        productConfigSessionCustVals1 = self.env[
            "product.config.session.custom.value"
        ].create(
            {
                "cfg_session_id": self.session_id.id,
                "attribute_id": self.attr_color.id,
                "attachment_ids": [(6, 0, [self.irAttachement.id])],
            }
        )
        checkBinaryval = self.session_id._get_custom_vals_dict()
        attr_id = productConfigSessionCustVals1.attribute_id.id
        self.assertEqual(
            checkBinaryval.get(attr_id),
            productConfigSessionCustVals1.attachment_ids,
            "Error: If Not attachement\
            Method: _get_custom_vals_dict()",
        )

    def test_06_compute_config_step_name(self):
        self.config_session._compute_config_step_name()
        self.assertTrue(
            self.config_session.config_step_name,
            "Error: If not config step name\
            Method: _compute_config_step_name()",
        )
        self.config_session._compute_config_step_name()
        self.assertEqual(
            self.config_session.config_step_name,
            "Extras",
            "Error: If not equal config_step_name and config_step\
            Method: _compute_config_step_name()",
        )
        session = self.productConfigSession.create(
            {
                "product_tmpl_id": self.config_product.id,
                "value_ids": [
                    (6, 0, [self.value_gasoline.id, self.value_transmission.id])
                ],
                "user_id": self.env.user.id,
            }
        )
        session._compute_config_step_name()
        self.assertFalse(
            session.config_step_name,
            "Error: If config_step_name not False\
            Method: _compute_config_step_name()",
        )

    def test_07_search_variant(self):
        with self.assertRaises(ValidationError):
            self.env["product.config.session"].search_variant()

        # check for search duplicate variant
        variant_id = self.config_product.product_variant_ids
        checkSearchvarient = self.config_session.search_variant()
        self.assertEqual(
            checkSearchvarient,
            variant_id,
            "Error: If Not Equal Variant or False\
            Method: search_variant()",
        )

    def test_08_check_custom_type(self):
        # check for check_custom_type
        with self.assertRaises(ValidationError):
            self.env["product.config.session.custom.value"].create(
                {
                    "attribute_id": self.value_silver.attribute_id.id,
                    "cfg_session_id": self.config_session.id,
                    "value": "Test",
                    "attachment_ids": [(6, 0, [self.irAttachement.id])],
                }
            )

        self.attr_color.custom_type = "binary"
        with self.assertRaises(ValidationError):
            self.env["product.config.session.custom.value"].create(
                {
                    "attribute_id": self.value_silver.attribute_id.id,
                    "cfg_session_id": self.config_session.id,
                    "value": "Test",
                    "attachment_ids": [(6, 0, [self.irAttachement.id])],
                }
            )

    def test_09_create_get_variant(self):
        # configure new product to check for search not dublicate variant
        attributeLine1 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_1.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_1.id, self.attribute_vals_2.id])
                ],
            }
        )
        # create attribute line 2
        attributeLine2 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_2.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_3.id, self.attribute_vals_4.id])
                ],
            }
        )
        self.product_tmpl_id.write(
            {
                "attribute_line_ids": [(6, 0, [attributeLine1.id, attributeLine2.id])],
            }
        )
        self.product_tmpl_id.configure_product()
        self.productConfWizard.action_next_step()
        product_config_wizard = self.productConfWizard.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                f"__attribute_{self.attribute_1.id}": self.attribute_vals_1.id,
                f"__attribute_{self.attribute_2.id}": self.attribute_vals_3.id,
            }
        )
        product_config_wizard.action_next_step()
        config_session_1 = self.productConfigSession.search(
            [("product_tmpl_id", "=", self.product_tmpl_id.id)]
        )
        createVarientId = config_session_1.create_get_variant()
        self.assertEqual(
            createVarientId.name,
            self.product_tmpl_id.name,
            "Error: If Not Equal variant name\
            Method: search_variant()",
        )
        # FIXME: broken when running `attributeLine1.custom = True`
        #   """
        #   psycopg2.errors.UniqueViolation:
        #   duplicate key value violates unique constraint
        #   "product_product_combination_unique"
        #   DETAIL:  Key (product_tmpl_id, combination_indices)=(81, 459,461)
        #       already exists.
        # attributeLine1.custom = True
        # self.env["product.config.session.custom.value"].create(
        #     {
        #         "cfg_session_id": config_session_1.id,
        #         "attribute_id": self.attribute_1.id,
        #         "value": "Coke",
        #     }
        # )
        # config_session_1.create_get_variant()

    def test_10_check_value_ids(self):
        with self.assertRaises(ValidationError):
            self.config_image_red.write(
                {"value_ids": [(6, 0, [self.value_gasoline.id, self.value_diesel.id])]}
            )

    def test_11_unique_attribute(self):
        with self.assertRaises(ValidationError):
            self.env["product.config.session.custom.value"].create(
                {
                    "cfg_session_id": self.config_session.id,
                    "attribute_id": self.attr_engine.id,
                    "value": "1234",
                }
            )
            self.env["product.config.session.custom.value"].create(
                {
                    "cfg_session_id": self.config_session.id,
                    "attribute_id": self.attr_engine.id,
                    "value": "1234",
                }
            )

    # FIXME: broken at the first create as
    #   """
    #   psycopg2.errors.NotNullViolation
    #     null value in column "attribute_line_id" of
    #     relation "product_template_attribute_value"
    #     violates not-null constraint
    #   DETAIL:  Failing row contains ...
    # def test_12_get_cfg_weight(self):
    #     self.env["product.template.attribute.value"].create(
    #         {
    #             "product_tmpl_id": self.config_product.id,
    #             "product_attribute_value_id": self.value_red.id,
    #             "weight_extra": 20.0,
    #         }
    #     )
    #     self.config_product.weight = 20
    #     weightVal = self.config_session.get_cfg_weight()
    #     self.assertEqual(
    #         weightVal,
    #         40.0,
    #         "Error: If Value are not equal\
    #         Method: get_cfg_weight()",
    #     )
    #     # check for config weight
    #     self.assertEqual(
    #         self.config_session.weight,
    #         40.0,
    #         "Error: If config weight are not equal\
    #         Method: _compute_cfg_weight()",
    #     )

    def test_13_update_session_configuration_value(self):
        # configure new product to check for search not dublicate variant
        self.custom_vals = self.productConfigSession.get_custom_value_id()
        self.attributeLine1 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_1.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_1.id, self.attribute_vals_2.id])
                ],
                "custom": True,
                "required": True,
            }
        )
        # create attribute line 2
        self.attributeLine2 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_2.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_3.id, self.attribute_vals_4.id])
                ],
                "custom": True,
                "required": True,
            }
        )
        self.product_tmpl_id.write(
            {
                "attribute_line_ids": [
                    (6, 0, [self.attributeLine1.id, self.attributeLine2.id])
                ],
            }
        )
        self.attribute_1.custom_type = "binary"
        self.product_tmpl_id.configure_product()
        self.productConfWizard.action_next_step()
        product_config_wizard = self.productConfWizard.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                f"__attribute_{self.attribute_1.id}": self.custom_vals.id,
                f"__custom_{self.attribute_1.id}": "Test",
            }
        )
        # FIXME: broken validation at `product_config.create_get_variant`
        #   """
        #   odoo.exceptions.ValidationError: Required attribute 'Flavour' is empty
        # product_config_wizard.action_next_step()

    # FIXME: broken at the first create as
    #   """
    #   psycopg2.errors.NotNullViolation
    #     null value in column "attribute_line_id" of
    #     relation "product_template_attribute_value"
    #     violates not-null constraint
    #   DETAIL:  Failing row contains ...
    # def test_14_get_cfg_price(self):
    #     self.env["product.template.attribute.value"].create(
    #         {
    #             "product_tmpl_id": self.config_product.id,
    #             "product_attribute_value_id": self.value_red.id,
    #             "weight_extra": 20.0,
    #             "price_extra": 20.0,
    #         }
    #     )
    #     price = self.config_product.list_price
    #     price += self.value_220i.product_id.lst_price
    #     price += self.value_model_sport_line.product_id.lst_price
    #     price += self.value_transmission.product_id.lst_price
    #     price += self.value_options_2.product_id.lst_price
    #     price_extra_val = self.session_id.get_cfg_price()
    #     self.assertEqual(
    #         price_extra_val,
    #         price + 20,
    #         "Error: If not equal price extra\
    #         Method: get_cfg_price()",
    #     )

    def test_15_get_next_step(self):
        self.session_id.get_next_step(state=None)
        self.session_id.get_next_step(state="draft")
        with self.assertRaises(UserError):
            self.productConfigSession.get_next_step(
                state="draft", value_ids=False, custom_value_ids=False
            )

    def test_16_get_all_step_lines(self):
        step_line_value_1 = self.productConfigSession.get_all_step_lines()
        self.assertFalse(
            step_line_value_1,
            "Error: If return True\
            Method: get_all_step_lines()",
        )
        step_line_value_2 = self.session_id.get_all_step_lines()
        self.assertTrue(
            step_line_value_2,
            "Error: If return True\
            Method: get_all_step_lines()",
        )

    def test_17_custom_value_validate_configuration(self):
        self.custom_vals = self.productConfigSession.get_custom_value_id()
        self.attributeLine1 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_1.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_1.id, self.attribute_vals_2.id])
                ],
                "custom": True,
                "required": True,
            }
        )
        # create attribute line 2
        self.attributeLine2 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_2.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_3.id, self.attribute_vals_4.id])
                ],
                "custom": True,
                "required": True,
            }
        )
        self.product_tmpl_id.write(
            {
                "attribute_line_ids": [
                    (6, 0, [self.attributeLine1.id, self.attributeLine2.id])
                ],
            }
        )
        self.attribute_1.custom_type = "binary"
        self.product_tmpl_id.configure_product()
        self.productConfWizard.action_next_step()
        product_config_wizard = self.productConfWizard.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                f"__attribute_{self.attribute_1.id}": self.custom_vals.id,
                f"__custom_{self.attribute_1.id}": "Test",
            }
        )
        self.attributeLine1.custom = False
        self.attributeLine2.custom = False
        with self.assertRaises(ValidationError):
            self.product_tmpl_id.configure_product()

    def test_18_onchange_attribute(self):
        # create domain
        self.productConfigDomainId = self.env["product.config.domain"].create(
            {"name": "restriction 1"}
        )
        self.productConfigDomainId.compute_domain()
        # create attribute value line 1
        self.env["product.config.domain.line"].create(
            {
                "domain_id": self.productConfigDomainId.id,
                "attribute_id": self.attr_fuel.id,
                "condition": "in",
                "value_ids": [(6, 0, [self.value_gasoline.id])],
                "operator": "and",
            }
        )
        self.env["product.config.domain.line"].create(
            {
                "domain_id": self.productConfigDomainId.id,
                "attribute_id": self.attr_color.id,
                "condition": "in",
                "value_ids": [(6, 0, [self.value_red.id])],
                "operator": "and",
            }
        )
        self.attributeLine1 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_1.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_1.id, self.attribute_vals_2.id])
                ],
                "required": True,
            }
        )
        # create attribute line 2
        self.attributeLine2 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attribute_2.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_3.id, self.attribute_vals_4.id])
                ],
                "required": True,
            }
        )
        self.product_tmpl_id.write(
            {
                "attribute_line_ids": [
                    (6, 0, [self.attributeLine1.id, self.attributeLine2.id])
                ],
            }
        )
        self.productConfigDomainId.compute_domain()
        # create attribute value line 1
        config_line = self.env["product.config.line"].create(  # noqa
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_line_id": self.attributeLine1.id,
                "value_ids": [
                    (6, 0, [self.attribute_vals_1.id, self.attribute_vals_2.id])
                ],
                "domain_id": self.productConfigDomainId.id,
            }
        )
        # FIXME: broken as
        #   """
        #   psycopg2.errors.NotNullViolation:
        #   null value in column "domain_id"
        #   of relation "product_config_line"
        #   violates not-null constraint
        #   DETAIL:  Failing row contains ...
        # with self.assertRaises(ValidationError):
        #     config_line.onchange_attribute()

        # self.assertFalse(
        #     config_line.value_ids,
        #     "Error: If value_ids True\
        #     Method: onchange_attribute()",
        # )

    def test_19_eval(self):
        self.attr_color.custom_type = "binary"
        productConfigSessionCustVals1 = self.env[
            "product.config.session.custom.value"
        ].create(
            {
                "cfg_session_id": self.session_id.id,
                "attribute_id": self.attr_color.id,
                "attachment_ids": [(6, 0, [self.irAttachement.id])],
            }
        )
        checkBinary = productConfigSessionCustVals1.eval()
        self.assertTrue(
            checkBinary,
            "Error: If value False\
            Method: eval()",
        )

        productConfigSessionCustVals = self.env[
            "product.config.session.custom.value"
        ].create(
            {"cfg_session_id": self.session_id.id, "attribute_id": self.attr_fuel.id}
        )
        self.attr_fuel.custom_type = "integer"
        productConfigSessionCustVals.update({"value": 154})
        checkIntval = productConfigSessionCustVals.eval()
        self.assertEqual(
            154,
            checkIntval,
            "Error: If Value not equal\
            Method: eval()",
        )

        self.attr_fuel.custom_type = "float"
        productConfigSessionCustVals.update({"value": 15.4})
        checkfloat = productConfigSessionCustVals.eval()
        self.assertEqual(
            15.4,
            checkfloat,
            "Error: If Value not equal\
            Method: eval()",
        )

    def test_20_values_available(self):
        check_available_val_ids = (
            self.value_gasoline + self.value_218i + self.value_sport_line
        ).ids
        product_tmpl_id = self.config_product.id
        values_ids = [self.value_diesel.id]
        available_value_ids = self.productConfigSession.values_available(
            check_available_val_ids, values_ids, {}, product_tmpl_id
        )
        self.assertNotIn(
            self.value_sport_line.id,
            available_value_ids,
            "Error: If value exists\
            Method: values_available()",
        )
