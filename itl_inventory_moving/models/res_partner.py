from odoo import api, fields, models, tools, SUPERUSER_ID, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    itl_is_logistic_company = fields.Boolean("Logistic company")
    itl_is_warehouse_contact = fields.Boolean("Warehouse contact")
    itl_is_employee = fields.Boolean("Is employee")
    
    # Inherit
    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_address(self):
        for partner in self:
            if self.env.context.get('without_company'):
                partner.contact_address = partner._display_address(without_company=self.env.context.get('without_company'))
    
    # Inherit
    def _get_contact_name(self, partner, name):
        if self._context.get('show_contact_only'):
            return "%s" % (name)
        else:
            return "%s, %s" % (partner.commercial_company_name or partner.sudo().parent_id.name, name)