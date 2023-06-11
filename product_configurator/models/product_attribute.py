from ast import literal_eval

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        new_attrs = self.env['product.attribute']
        for attr in self:
            default.update({'name': attr.name + " (copy)"})
            new_attrs += super(ProductAttribute, attr).copy(default)
        return new_attrs

    @api.model
    def _get_nosearch_fields(self):
        """Return a list of custom field types that do not support searching"""
        return ['binary']

    @api.onchange('custom_type')
    def onchange_custom_type(self):
        if self.custom_type in self._get_nosearch_fields():
            self.search_ok = False
        if self.custom_type not in ('int', 'float'):
            self.min_val = False
            self.max_val = False

    @api.onchange('val_custom')
    def onchange_val_custom_field(self):
        if not self.val_custom:
            self.custom_type = False

    CUSTOM_TYPES = [
        ('char', 'Char'),
        ('int', 'Integer'),
        ('float', 'Float'),
        ('text', 'Textarea'),
        ('color', 'Color'),
        ('binary', 'Attachment'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
    ]

    active = fields.Boolean(
        string='Active',
        default=True,
        help='By unchecking the active field you can '
        'disable a attribute without deleting it'
    )

    min_val = fields.Integer(string="Min Value", help="Minimum value allowed")
    max_val = fields.Integer(string="Max Value", help="Minimum value allowed")

    # TODO: Exclude self from result-set of dependency
    val_custom = fields.Boolean(
        string='Custom Value',
        help='Allow custom value for this attribute?'
    )
    custom_type = fields.Selection(
        selection=CUSTOM_TYPES,
        string='Field Type',
        size=64,
        help='The type of the custom field generated in the frontend'
    )

    description = fields.Text(string='Description', translate=True)

    search_ok = fields.Boolean(
        string='Searchable',
        help='When checking for variants with '
        'the same configuration, do we '
        'include this field in the search?'
    )
    required = fields.Boolean(
        string='Required',
        default=True,
        help='Determines the required value of this '
        'attribute though it can be change on '
        'the template level'
    )
    multi = fields.Boolean(
        string="Multi",
        help='Allow selection of multiple values for '
        'this attribute?'
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Unit of Measure'
    )
    image = fields.Binary(string='Image')

    # TODO prevent the same attribute from being defined twice on the
    # attribute lines

    _order = 'sequence'

    @api.constrains('custom_type', 'search_ok')
    def check_searchable_field(self):
        nosearch_fields = self._get_nosearch_fields()
        if self.custom_type in nosearch_fields and self.search_ok:
            raise ValidationError(
                _("Selected custom field type '%s' is not searchable" %
                  self.custom_type)
            )

    def validate_custom_val(self, val):
        """ Pass in a desired custom value and ensure it is valid.
        Probaly should check type, etc, but let's assume fine for the moment.
        """
        self.ensure_one()
        if self.custom_type in ('int', 'float'):
            minv = self.min_val
            maxv = self.max_val
            val = literal_eval(str(val))
            if minv and maxv and (val < minv or val > maxv):
                raise ValidationError(
                    _("Selected custom value '%s' must be between %s and %s"
                        % (self.name, self.min_val, self.max_val))
                )
            elif minv and val < minv:
                raise ValidationError(
                    _("Selected custom value '%s' must be at least %s" %
                        (self.name, self.min_val))
                )
            elif maxv and val > maxv:
                raise ValidationError(
                    _("Selected custom value '%s' must be lower than %s" %
                        (self.name, self.max_val + 1))
                )

    @api.constrains('min_val', 'max_val')
    def _check_constraint_min_max_value(self):
        if self.custom_type not in ('int', 'float'):
            return
        minv = self.min_val
        maxv = self.max_val
        if maxv and minv and maxv < minv:
            raise ValidationError(
                _("Maximum value must be greater than Minimum value"))


class ProductAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    @api.onchange('attribute_id')
    def onchange_attribute(self):
        self.value_ids = False
        self.required = self.attribute_id.required
        self.multi = self.attribute_id.multi
        self.custom = self.attribute_id.val_custom
        # TODO: Remove all dependencies pointed towards the attribute being
        # changed

    @api.onchange('value_ids')
    def onchange_values(self):
        if self.default_val and self.default_val not in self.value_ids:
            self.default_val = None

    custom = fields.Boolean(
        string='Custom',
        help="Allow custom values for this attribute?"
    )
    required = fields.Boolean(
        string='Required',
        help="Is this attribute required?"
    )
    multi = fields.Boolean(
        string='Multi',
        help='Allow selection of multiple values for this attribute?'
    )
    default_val = fields.Many2one(
        comodel_name='product.attribute.value',
        string='Default Value'
    )

    sequence = fields.Integer(string='Sequence', default=10)

    # TODO: Order by dependencies first and then sequence so dependent fields
    # do not come before master field
    _order = 'product_tmpl_id, sequence, id'

    # TODO: Constraint not allowing introducing dependencies that do not exist
    # on the product.template

    @api.multi
    @api.constrains('value_ids', 'default_val')
    def _check_default_values(self):
        for line in self.filtered(lambda l: l.default_val):
            if line.default_val not in line.value_ids:
                raise ValidationError(
                    _("Default values for each attribute line must exist in "
                      "the attribute values (%s: %s)" % (
                          line.attribute_id.name, line.default_val.name)
                      )
                )


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        default.update({'name': self.name + " (copy)"})
        product = super(ProductAttributeValue, self).copy(default)
        return product

    @api.multi
    def _compute_price_ids(self):
        for value in self:
            att_line = self.env['product.template.attribute.line']
            att_line_val = att_line.search([('value_ids', '=', value.id)])
            value.price_ids = att_line_val.product_template_value_ids

    price_ids = fields.Many2many('product.template.attribute.value', compute="_compute_price_ids")

    @api.multi
    def _compute_weight_extra(self):
        for product_attribute in self:
            product_tmpl_id = product_attribute._context.get('active_id')
            if product_tmpl_id:
                price = product_attribute.price_ids.filtered(
                    lambda price: price.product_tmpl_id.id == product_tmpl_id
                )
                product_attribute.weight_extra = price.weight_extra
            else:
                product_attribute.weight_extra = 0.0

    def _inverse_weight_extra(self):
        product_tmpl_id = self._context.get('active_id')
        if not product_tmpl_id:
            return

        AttributePrice = self.env['product.attribute.price']
        prices = AttributePrice.search([
            ('value_id', 'in', self.ids),
            ('product_tmpl_id', '=', product_tmpl_id)
        ])
        updated = prices.mapped('value_id')
        if prices:
            prices.write({'weight_extra': self.weight_extra})
        else:
            for value in self - updated:
                AttributePrice.create({
                    'product_tmpl_id': product_tmpl_id,
                    'value_id': value.id,
                    'weight_extra': self.weight_extra,
                })

    active = fields.Boolean(
        string='Active',
        default=True,
        help='By unchecking the active field you can '
        'disable a attribute value without deleting it'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Related Product'
    )
    attribute_line_ids = fields.Many2many(
        comodel_name='product.attribute.line',
        string="Attribute Lines",
        copy=False
    )
    weight_extra = fields.Float(
        string='Attribute Weight Extra',
        compute='_compute_weight_extra',
        inverse='_inverse_weight_extra',
        default=0.0,
        digits=dp.get_precision('Product Weight'),
        help="Weight Extra: Extra weight for the variant with this attribute"
        "value on sale price. eg. 200 price extra, 1000 + 200 = 1200."
    )
    # prevent to add new attr-value from adding
    # in already created template
    product_ids = fields.Many2many(
        comodel_name='product.product',
        copy=False
    )

    @api.multi
    def name_get(self):
        res = super(ProductAttributeValue, self).name_get()
        if not self._context.get('show_price_extra'):
            return res
        extra_prices = {
            av.id: av.price_extra for av in self if av.price_extra
        }

        res_prices = []

        for val in res:
            price_extra = extra_prices.get(val[0])
            if price_extra:
                val = (val[0], '%s ( +%s )' % (val[1], price_extra))
            res_prices.append(val)
        return res_prices

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Use name_search as a domain restriction for the frontend to show
        only values set on the product template taking all the configuration
        restrictions into account.

        TODO: This only works when activating the selection not when typing
        """
        product_tmpl_id = self.env.context.get('_cfg_product_tmpl_id')
        if product_tmpl_id:
            # TODO: Avoiding browse here could be a good performance enhancer
            product_tmpl = self.env['product.template'].browse(product_tmpl_id)
            tmpl_vals = product_tmpl.attribute_line_ids.mapped('value_ids')
            attr_restrict_ids = []
            preset_val_ids = []
            new_args = []
            for arg in args:
                # Restrict values only to value_ids set on product_template
                if arg[0] == 'id' and arg[1] == 'not in':
                    preset_val_ids = arg[2]
                    # TODO: Check if all values are available for configuration
                else:
                    new_args.append(arg)
            val_ids = set(tmpl_vals.ids)
            if preset_val_ids:
                val_ids -= set(arg[2])
            val_ids = self.env['product.config.session'].values_available(
                val_ids, preset_val_ids, product_tmpl_id=product_tmpl_id)
            new_args.append(('id', 'in', val_ids))
            mono_tmpl_lines = product_tmpl.attribute_line_ids.filtered(
                lambda l: not l.multi)
            for line in mono_tmpl_lines:
                line_val_ids = set(line.mapped('value_ids').ids)
                if line_val_ids & set(preset_val_ids):
                    attr_restrict_ids.append(line.attribute_id.id)
            if attr_restrict_ids:
                new_args.append(('attribute_id', 'not in', attr_restrict_ids))
            args = new_args
        res = super(ProductAttributeValue, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        return res

    # TODO: Prevent unlinking custom options by overriding unlink

    # _sql_constraints = [
    #    ('unique_custom', 'unique(id,allow_custom_value)',
    #    'Only one custom value per dimension type is allowed')
    # ]


class ProductAttributePrice(models.Model):
    _inherit = "product.template.attribute.value"
    # Leverage product.attribute.price to compute the extra weight each
    # attribute adds

    weight_extra = fields.Float(
        string="Weight",
        digits=dp.get_precision('Product Weight')
    )


class ProductAttributeValueLine(models.Model):
    _name = 'product.attribute.value.line'

    sequence = fields.Integer(string='Sequence', default=10)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        ondelete='cascade',
        required=True
    )
    value_id = fields.Many2one(
        comodel_name='product.attribute.value',
        required="True",
        string="Attribute Value",
    )
    attribute_id = fields.Many2one(
        comodel_name='product.attribute',
        related='value_id.attribute_id',
    )
    value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        relation="product_attribute_value_product_attribute_value_line_rel",
        column1="product_attribute_value_line_id",
        column2="product_attribute_value_id",
        string="Values Configuration",
    )
    product_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        relation="product_attr_values_attr_values_rel",
        column1="product_val_id",
        column2="attr_val_id",
        compute='_compute_get_value_id',
        store=True
    )

    @api.multi
    @api.depends('product_tmpl_id', 'product_tmpl_id.attribute_line_ids',
                 'product_tmpl_id.attribute_line_ids.value_ids')
    def _compute_get_value_id(self):
        for attr_val_line in self:
            template = attr_val_line.product_tmpl_id
            value_list = template.attribute_line_ids.mapped('value_ids')
            attr_val_line.product_value_ids = [(6, 0, value_list.ids)]

    _order = 'sequence'

    @api.multi
    @api.constrains('value_ids')
    def _validate_configuration(self):
        """Ensure that the passed configuration in value_ids is a valid"""
        cfg_session_obj = self.env['product.config.session']
        for attr_val_line in self:
            value_ids = attr_val_line.value_ids.ids
            value_ids.append(attr_val_line.value_id.id)
            valid = cfg_session_obj.validate_configuration(
                value_ids=value_ids,
                product_tmpl_id=attr_val_line.product_tmpl_id.id,
                final=False
            )
            if not valid:
                raise ValidationError(
                    _('Values provided to the attribute value line are '
                      'incompatible with the current rules')
                )


class ProductAttributeValueCustom(models.Model):

    @api.multi
    @api.depends('attribute_id', 'attribute_id.uom_id')
    def _compute_val_name(self):
        for attr_val_custom in self:
            uom = attr_val_custom.attribute_id.uom_id.name
            attr_val_custom.name = '%s%s' % (attr_val_custom.value, uom or '')

    _name = 'product.attribute.value.custom'

    name = fields.Char(
        string='Name',
        readonly=True,
        compute="_compute_val_name",
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product ID',
        required=True,
        ondelete='cascade'
    )
    attribute_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Attribute',
        required=True
    )
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='product_attr_val_custom_value_attachment_rel',
        column1='attr_val_custom_id',
        column2='attachment_id',
        string='Attachments'
    )
    value = fields.Char(
        string='Custom Value',
    )

    _sql_constraints = [
        ('attr_uniq', 'unique(product_id, attribute_id)',
         'Cannot have two custom values for the same attribute')
    ]
