from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductConfigWebsiteRestriction(WebsiteSale):

    def get_config_session(self, product_tmpl_id):
        cfg_session_obj = request.env["product.config.session"]
        cfg_session = False
        product_config_sessions = request.session.get("product_config_session", {})
        is_public_user = request.env.user.has_group("base.group_public")
        cfg_session_id = product_config_sessions.get(product_tmpl_id.id)
        if cfg_session_id:
            cfg_session = cfg_session_obj.browse(int(cfg_session_id))

        # Retrieve an active configuration session or create a new one
        if not cfg_session or not cfg_session.exists():
            cfg_session = cfg_session_obj.sudo().create_get_session(
                product_tmpl_id.id,
                force_create=is_public_user,
                user_id=request.env.user.id,
            )
            product_config_sessions.update({product_tmpl_id.id: cfg_session.id})
            request.session["product_config_session"] = product_config_sessions

        if cfg_session.user_id.has_group("base.group_public") and not is_public_user:
            cfg_session.user_id = request.env.user
        return cfg_session

    @http.route()
    def product(self, product, category="", search="", **kwargs):
        # Use parent workflow for regular products
        return super(ProductConfigWebsiteRestriction, self).product(
            product, category, search, **kwargs
        )

    def convert_form_data(self, form_data):
        """convert the form data ptal to attribute"""
        ProductAttributeLine = request.env['product.template.attribute.line']
        form_values = []
        ptal_count = 0

        for item in form_data:
            name = item.get('name')
            value = item.get('value')

            # Map product_template_id
            if name == 'product_template_id':
                form_values.append({'name': 'product_tmpl_id', 'value': value})

            # Map product_id
            if name == 'product_id':
                form_values.append({'name': 'product_id', 'value': value})

            # Map each ptal-* line to __attribute-<attribute_id>
            elif name.startswith('ptal-') and value:
                ptal_id = int(name.split('-')[1])
                ptal = ProductAttributeLine.browse(ptal_id)
                if ptal.exists():
                    attribute_id = ptal.attribute_id.id
                    form_values.append({'name': f'__attribute-{attribute_id}', 'value': value})
                    ptal_count += 1

        # Optionally fill in empty attributes (not selected)
        product_tmpl_id = next((i['value'] for i in form_data if i['name'] == 'product_template_id'), False)
        if product_tmpl_id:
            ptal_lines = ProductAttributeLine.search([('product_tmpl_id', '=', int(product_tmpl_id))])
            for ptal in ptal_lines:
                key = f'__attribute-{ptal.attribute_id.id}'
                if not any(fv['name'] == key for fv in form_values):
                    form_values.append({'name': key, 'value': ''})  # empty value

            form_values.append({'name': 'total_attributes', 'value': str(len(ptal_lines))})

        print('\n\n form_values------------', form_values)
        return form_values

    def _prepare_configurator_values(self, form_vals, config_session_id):
        """Return dictionary of fields and values present
        on configuration wizard"""
        config_session_id = config_session_id.sudo()
        product_tmpl_id = config_session_id.product_tmpl_id
        config_fields = {
            "state": config_session_id.state,
            "config_session_id": config_session_id.id,
            "product_tmpl_id": product_tmpl_id.id,
            "product_preset_id": config_session_id.product_preset_id.id,
            "price": config_session_id.price,
            "value_ids": [[6, False, config_session_id.value_ids.ids]],
            "attribute_line_ids": [
                [4, line.id, False] for line in product_tmpl_id.attribute_line_ids
            ],
        }
        config_fields.update(form_vals)
        return config_fields

    def get_restrict_orm_form_vals(self, form_vals, config_session):
        """Return dictionary of dynamic field and its values
        :param: form_vals: list of dictionary
            Ex: [{'name': field-name, 'value': field-value},]
        :param: cfg_session: record set of config session"""

        product_tmpl_id = config_session.product_tmpl_id
        values = {}
        for form_val in form_vals:
            dict_key = form_val.get("name", False)
            dict_value = form_val.get("value", False)
            if not dict_key or not dict_value:
                continue
            if dict_key not in values:
                values.update({dict_key: []})
            values[dict_key].append(dict_value)

        product_configurator_obj = request.env["product.configurator"]
        field_prefix = product_configurator_obj._prefixes.get("field_prefix")
        custom_field_prefix = product_configurator_obj._prefixes.get(
            "custom_field_prefix"
        )

        config_vals = {}
        for attr_line in product_tmpl_id.attribute_line_ids.sorted():
            attribute_id = attr_line.attribute_id.id
            field_name = "%s%s" % (field_prefix, attribute_id)
            custom_field = "%s%s" % (custom_field_prefix, attribute_id)

            field_value = values.get(field_name, [])
            field_value = [int(s) for s in field_value]
            custom_field_value = values.get(custom_field, False)

            if attr_line.custom and custom_field_value:
                custom_field_value = custom_field_value[0]
                if attr_line.attribute_id.custom_type in ["int", "float"]:
                    custom_field_value = safe_eval(custom_field_value)

            if attr_line.multi:
                field_value = [[6, False, field_value]]
            else:
                field_value = field_value and field_value[0] or False

            config_vals.update(
                {field_name: field_value, custom_field: custom_field_value}
            )
        return config_vals

    def convert_data_domain(self, domain):
        new_domain = {}

        for key, domain_list in domain.items():
            if not key.startswith('__attribute-') or not domain_list:
                continue

            domain_operator = domain_list[0][1]
            value_ids = domain_list[0][2]

            # Convert to records (even if empty list)
            value_records = request.env['product.attribute.value'].browse(value_ids)

            # Ensure we can fetch attribute
            if value_records:
                attribute = value_records[0].attribute_id
            else:
                # If no values, infer attribute ID from the key (e.g. '__attribute-2' → 2)
                try:
                    attribute_id = int(key.replace('__attribute-', ''))
                    attribute = request.env['product.attribute'].browse(attribute_id)
                except Exception:
                    continue  # Skip if we can't safely parse

            if not attribute or not attribute.exists():
                continue

            attribute_name = attribute.name
            all_values = attribute.value_ids.mapped('name')
            allowed_values = value_records.mapped('name') if value_records else []

            new_domain[attribute_name] = [all_values, allowed_values, domain_operator]

        return new_domain


    @http.route(['/check/configurator/restriction'], type='json', auth="user", methods=['POST'])
    def check_exist_product(self, product_template_id=False, attribute_id=False, ptav_id=False, form_data={}):
        """ bypass custom value product create time from sale product configurator"""
        product_configurator_obj = request.env["product.configurator"]
        product_template_id = request.env['product.template'].browse(int(product_template_id))
        print('\n\n product_template_id----------------', product_template_id)
        if not product_template_id or not (product_template_id and product_template_id.config_ok):
            print('\n\n False template----------------', product_template_id.config_ok)
            return False
        # prepare dictionary in formate needed to pass in onchage
        form_values = self.convert_form_data(form_data)
        attribute_id = request.env['product.attribute'].browse(int(attribute_id))

        try:
            config_session_id = self.get_config_session(product_tmpl_id=product_template_id)
        except Exception:
            pass

        if config_session_id:
            # prepare dictionary in formate needed to pass in onchage
            form_values = self.get_restrict_orm_form_vals(form_values, config_session_id)
            # Filter only keys starting with '__attribute-'
            attribute_keys = [key for key in form_values if key.startswith('__attribute-')]
            # Convert template value IDs to attribute value IDs
            for key in attribute_keys:
                ptav_id = form_values[key]
                if ptav_id:
                    ptav = request.env['product.template.attribute.value'].browse(int(ptav_id))
                    pav_id = ptav.product_attribute_value_id.id if ptav.product_attribute_value_id else False
                    form_values[key] = pav_id  # Replace the value in the original dict
            # Config values
            config_vals = self._prepare_configurator_values(form_values, config_session_id)

            # call onchange
            specs = product_configurator_obj._onchange_spec()
            form_domain = {}
            try:
                field_name = f'__attribute-{attribute_id.id}'
                form_domain = product_configurator_obj.sudo().apply_onchange_values(
                    values=config_vals, field_name=field_name, field_onchange=specs
                )
                form_domain['domain'] = self.convert_data_domain(form_domain['domain'])
                form_domain['is_configured'] = product_template_id.config_ok
            except Exception:
                pass

        print('\n\n form_domain----------------', form_domain)
        return form_domain
