from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools import safe_eval


def get_pricelist():
    sale_order = request.env.context.get('sale_order')
    if sale_order:
        pricelist = sale_order.pricelist_id
    else:
        partner = request.env.user.partner_id
        pricelist = partner.property_product_pricelist
    return pricelist


class ProductConfigWebsiteSale(WebsiteSale):

    def get_config_session(self, product_tmpl_id):
        cfg_session_obj = request.env['product.config.session']
        cfg_session = False
        product_config_sessions = request.session.get(
            'product_config_session',
            {}
        )
        is_public_user = request.env.user.has_group('base.group_public')
        if (product_config_sessions and
                product_config_sessions.get(product_tmpl_id.id)):
            cfg_session = cfg_session_obj.browse(
                int(product_config_sessions.get(product_tmpl_id.id))
            )

        # Retrieve and active configuration session or create a new one
        if not cfg_session or not cfg_session.exists():
            cfg_session = cfg_session_obj.sudo().create_get_session(
                product_tmpl_id.id,
                force_create=is_public_user,
                user_id=request.env.user.id
            )
            if product_config_sessions:
                request.session['product_config_session'].update({
                    product_tmpl_id.id: cfg_session.id
                })
            else:
                request.session['product_config_session'] = {
                    product_tmpl_id.id: cfg_session.id
                }

        if (cfg_session.user_id.has_group('base.group_public') and not
                is_public_user):
            cfg_session.user_id = request.env.user
        return cfg_session

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        # Use parent workflow for regular products
        if not product.config_ok or not product.attribute_line_ids:
            return super(ProductConfigWebsiteSale, self).product(
                product, category, search, **kwargs
            )

        cfg_session = self.get_config_session(product_tmpl_id=product)

        # Set config-step in config session when it creates from wizard
        # because select state not exist on website
        if not cfg_session.config_step:
            cfg_session.config_step = 'select'
            self.set_config_next_step(cfg_session)

        # Render the configuration template based on the configuration session
        config_form = self.render_form(cfg_session)

        return config_form

    def get_render_vals(self, cfg_session):
        """Return dictionary with values required for website template
        rendering"""

        # if no config step exist
        product_configurator_obj = request.env['product.configurator']
        open_cfg_step_lines = cfg_session.get_open_step_lines()
        active_step = cfg_session.get_active_step()
        cfg_step_lines = cfg_session.get_all_step_lines()
        custom_ext_id = 'product_configurator.custom_attribute_value'
        custom_val_id = request.env.ref(custom_ext_id)
        check_val_ids = cfg_session.product_tmpl_id.attribute_line_ids.mapped(
            'value_ids') + custom_val_id
        available_value_ids = cfg_session.values_available(
            check_val_ids=check_val_ids.ids)
        if not active_step:
            active_step = cfg_step_lines[:1]
        extra_attribute_line_ids = self.get_extra_attribute_line_ids(
            cfg_session.product_tmpl_id)
        cfg_session = cfg_session.sudo()
        attr_val_line_ids = cfg_session.attribute_value_line_ids.ids
        vals = {
            'cfg_session': cfg_session,
            'cfg_step_lines': cfg_step_lines,
            'open_cfg_step_lines': open_cfg_step_lines,
            'active_step': active_step,
            'value_ids': cfg_session.value_ids,
            'custom_value_ids': cfg_session.custom_value_ids,
            'available_value_ids': available_value_ids,
            'main_object': cfg_session.product_tmpl_id,
            'prefixes': product_configurator_obj._prefixes,
            'custom_val_id': custom_val_id,
            'extra_attribute_line_ids': extra_attribute_line_ids,
            'attribute_value_line_ids': attr_val_line_ids
        }
        return vals

    def render_form(self, cfg_session):
        """Render the website form for the given template and configuration
        session"""
        vals = self.get_render_vals(cfg_session)
        return request.render(
            'website_product_configurator.product_configurator', vals
        )

    def remove_recursive_list(self, values):
        """Return dictionary by removing extra list
        :param: values: dictionary having values in form [[4, 0, [2, 3]]]
        :return: dictionary
        EX- {2: [2, 3]}"""
        new_values = {}
        for key, value in values.items():
            if isinstance(value, tuple):
                value = value[0]
            if isinstance(value, list):
                value = value[0][2]
            new_values[key] = value
        return new_values

    def get_current_configuration(self, form_values, cfg_session):
        """Return list of ids of selected attribute-values
        :param: form_values: dictionary of field name and selected values
            Ex: {
                __attribute-attr-id: attribute-value,
                __custom-attr-id: custom-value
            }
        :param: cfg_session: record set of config session"""

        product_tmpl_id = cfg_session.product_tmpl_id
        product_configurator_obj = request.env['product.configurator']
        field_prefix = product_configurator_obj._prefixes.get('field_prefix')
        # custom_field_prefix = product_configurator_obj._prefixes.get(
        #    'custom_field_prefix')

        product_attribute_lines = product_tmpl_id.attribute_line_ids
        value_ids = []
        for attr_line in product_attribute_lines:
            if attr_line.custom:
                pass
            else:
                field_name = '%s%s' % (field_prefix, attr_line.attribute_id.id)
                attr_values = form_values.get(field_name, False)

                if not attr_values:
                    continue
                if not isinstance(attr_values, list):
                    attr_values = [attr_values]
                elif isinstance(attr_values[0], list):
                    attr_values = attr_values[0][2]
                value_ids += attr_values
        return value_ids

    def _prepare_configurator_values(self, form_vals, config_session_id):
        """Return dictionary of fields and values present
        on configuration wizard"""
        config_session_id = config_session_id.sudo()
        product_tmpl_id = config_session_id.product_tmpl_id
        config_fields = {
            'state': config_session_id.state,
            'config_session_id': config_session_id.id,
            'product_tmpl_id': product_tmpl_id.id,
            'product_preset_id': config_session_id.product_preset_id.id,
            'price': config_session_id.price,
            'value_ids': [[6, False, config_session_id.value_ids.ids]],
            'attribute_value_line_ids': [
                [4, line.id, False]
                for line in config_session_id.attribute_value_line_ids
            ],
            'attribute_line_ids': [
                [4, line.id, False]
                for line in product_tmpl_id.attribute_line_ids
            ],
        }
        config_fields.update(form_vals)
        return config_fields

    def get_orm_form_vals(self, form_vals, config_session):
        """Return dictionary of dynamic field and its values
        :param: form_vals: list of dictionary
            Ex: [{'name': field-name, 'value': field-value},]
        :param: cfg_session: record set of config session"""

        product_tmpl_id = config_session.product_tmpl_id
        values = {}
        for form_val in form_vals:
            dict_key = form_val.get('name', False)
            dict_value = form_val.get('value', False)
            if not dict_key or not dict_value:
                continue
            if dict_key not in values:
                values.update({dict_key: []})
            values[dict_key].append(dict_value)

        product_configurator_obj = request.env['product.configurator']
        field_prefix = product_configurator_obj._prefixes.get('field_prefix')
        custom_field_prefix = product_configurator_obj._prefixes.get(
            'custom_field_prefix')

        config_vals = {}
        for attr_line in product_tmpl_id.attribute_line_ids.sorted():
            attribute_id = attr_line.attribute_id.id
            field_name = '%s%s' % (field_prefix, attribute_id)
            custom_field = '%s%s' % (custom_field_prefix, attribute_id)

            field_value = values.get(field_name, [])
            field_value = [int(s) for s in field_value]
            custom_field_value = values.get(custom_field, False)

            if attr_line.custom and custom_field_value:
                custom_field_value = custom_field_value[0]
                if attr_line.attribute_id.custom_type in ['int', 'float']:
                    custom_field_value = safe_eval(custom_field_value)

            if attr_line.multi:
                field_value = [[6, False, field_value]]
            else:
                field_value = field_value and field_value[0] or False

            config_vals.update({
                field_name: field_value,
                custom_field: custom_field_value,
            })
        return config_vals

    def get_config_product_template(self, form_vals):
        """Return record set of product template"""
        product_template_id = request.env['product.template']
        for val in form_vals:
            if val.get('name') == 'product_tmpl_id':
                product_tmpl_id = val.get('value')

        if product_tmpl_id:
            product_template_id = product_template_id.browse(
                int(product_tmpl_id))
        return product_template_id

    def get_extra_attribute_line_ids(self, product_template_id):
        """Retrieve attribute lines defined on the product_template_id
        which are not assigned to configuration steps"""

        extra_attribute_line_ids = (
            product_template_id.attribute_line_ids -
            product_template_id.config_step_line_ids.mapped(
                'attribute_line_ids'
            )
        )
        return extra_attribute_line_ids

    @http.route('/website_product_configurator/onchange',
                type='json', methods=['POST'], auth="public", website=True)
    def onchange(self, form_values, field_name):
        """Capture onchange events in the website and forward data to backend
        onchange method"""
        # config session and product template
        product_configurator_obj = request.env['product.configurator']
        product_template_id = self.get_config_product_template(form_values)
        config_session_id = self.get_config_session(
            product_tmpl_id=product_template_id)

        # prepare dictionary in formate needed to pass in onchage
        form_values = self.get_orm_form_vals(
            form_values, config_session_id)
        config_vals = self._prepare_configurator_values(
            form_values, config_session_id)

        # call onchange
        field_prefix = product_configurator_obj._prefixes.get('field_prefix')
        field_name = '%s%s' % (field_prefix, field_name)
        specs = product_configurator_obj._onchange_spec()
        updates = {}
        try:
            updates = product_configurator_obj.sudo().onchange(
                config_vals, field_name, specs)
        except Exception as Ex:
            return {'error': Ex}

        # get open step lines according to current configuation
        value_ids = self.get_current_configuration(
            form_values, config_session_id)
        try:
            open_cfg_step_line_ids = config_session_id.sudo()\
                .get_open_step_lines(value_ids).ids
        except Exception as Ex:
            return {'error': Ex}

        # if no step is defined or some attribute remains to add in a step
        open_cfg_step_line_ids = [
            '%s' % (step_id)
            for step_id in open_cfg_step_line_ids
        ]
        extra_attr_line_ids = self.get_extra_attribute_line_ids(
            product_template_id)
        if extra_attr_line_ids:
            open_cfg_step_line_ids.append('configure')

        updates['value'] = self.remove_recursive_list(updates['value'])
        updates['open_cfg_step_line_ids'] = open_cfg_step_line_ids
        return updates

    def set_config_next_step(self, config_session_id,
                             current_step=False, next_step=False):
        """Return next step of configuration wizard
        param: current_step: (string) current step of configuration wizard
        param: current_step: (string) next step of configuration wizard
            (in case when someone click on step directly instead
            of clicking on next button)
        return: (string) next step """
        config_session_id = config_session_id.sudo()
        extra_attr_line_ids = self.get_extra_attribute_line_ids(
            config_session_id.product_tmpl_id)
        if extra_attr_line_ids and current_step == 'configure':
            return next_step

        if not next_step:
            next_step = config_session_id.get_next_step(
                state=current_step,
            )
        if (not next_step and
                extra_attr_line_ids and
                current_step != 'configure'):
            next_step = 'configure'

        if not next_step:
            next_step = config_session_id.check_and_open_incomplete_step()
        if next_step and isinstance(
                next_step,
                type(request.env['product.config.step.line'])
        ):
            next_step = '%s' % (next_step.id)
        if next_step:
            config_session_id.config_step = next_step
        return next_step

    @http.route('/website_product_configurator/save_configuration',
                type='json', methods=['POST'], auth="public", website=True)
    def save_configuration(self, form_values, current_step=False,
                           next_step=False):
        """Save current configuration in related session and
        next step if exist otherwise create variant using
        configuration redirect to product page of configured product"""
        product_template_id = self.get_config_product_template(form_values)
        config_session_id = self.get_config_session(
            product_tmpl_id=product_template_id)

        form_values = self.get_orm_form_vals(
            form_values, config_session_id)
        try:
            # save values
            config_session_id.sudo().update_session_configuration_value(
                vals=form_values,
                product_tmpl_id=product_template_id
            )

            # next step
            next_step = self.set_config_next_step(
                config_session_id=config_session_id,
                current_step=current_step,
                next_step=next_step
            )
            if next_step:
                return {'next_step': next_step}

            # create variant
            product = config_session_id.sudo().create_get_variant()
            if product:
                config_session_id = config_session_id.sudo()
                redirect_url = "/website_product_configurator/open_product"
                redirect_url += '/%s' % (slug(config_session_id))
                redirect_url += '/%s' % (slug(product))
                return {
                    'product_id': product.id,
                    'config_session': config_session_id.id,
                    'redirect_url': redirect_url,
                }
        except Exception as Ex:
            return {'error': Ex}
        return {}

    @http.route(
        '/website_product_configurator/open_product/'
        '<model("product.config.session"):cfg_session>/'
        '<model("product.product"):product_id>',
        type='http', auth="public", website=True)
    def cfg_session(self, cfg_session, product_id, **post):
        """Render product page of product_id"""
        try:
            product_tmpl = cfg_session.sudo().product_tmpl_id
        except Exception:
            product_tmpl = product_id.product_tmpl_id

        def _get_product_vals(cfg_session):
            vals = cfg_session.value_ids
            # vals += cfg_session.custom_value_ids
            return sorted(vals, key=lambda obj: obj.attribute_id.sequence)

        pricelist = get_pricelist()
        values = {
            'get_product_vals': _get_product_vals,
            # 'get_config_image': self.get_config_image,
            'product_id': product_id,
            'product_tmpl': product_tmpl,
            'pricelist': pricelist,
            'cfg_session': cfg_session,
        }
        return request.render(
            "website_product_configurator.cfg_session", values)
