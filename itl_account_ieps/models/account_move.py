from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
	_inherit = 'account.move'
	
	itl_iesp_special = fields.Boolean(default=False)
	
	def post(self):
		for move in self:
			if move.type in ['out_invoice','out_refund']:
				line_ids = []
				line_ids, tax_ieps_id = move.get_extra_line_ieps()

				if len(line_ids) > 0:
					# adding the IEPS base journal line to line_ids
					move_line = self.env['account.move.line'].create(line_ids)
		return super(AccountMove, self).post()
	
	def get_extra_line_ieps(self):
		for move in self:
			line_ids = []
			is_ieps_tax = False
			tax_id = False
			for line in move.invoice_line_ids:
				for tax in line.tax_ids.flatten_taxes_hierarchy().filtered(lambda r: r.l10n_mx_cfdi_tax_type != 'Exento'):
					if tax.itl_include_in_tax:
						is_ieps_tax = True
						tax_id = tax
						move.itl_iesp_special = True
				if line.product_id and 'Pocari Sweat' in line.product_id.name:
					uom_id = line.product_uom_id
					product_qty = line.quantity
			if is_ieps_tax == True:
				new_ieps_account_id = False
				if move.type in ['out_invoice']:
					if 'Pocari' in move.line_ids[0].name:
						line = move.line_ids[0]

					amount = 0
					tax_ieps_id = False
					itl_uom_tax_id = move.company_id.itl_uom_tax_ids.filtered(lambda i: uom_id.id == i.itl_uom_id.id)
					if not itl_uom_tax_id:
						raise ValidationError("No se encontró la unidad de medida " + str(uom_id.name) + " dentro de la configuración especial de IEPS.")

					tax_ieps_id = itl_uom_tax_id.itl_tax_id

					if not tax_ieps_id:
						raise ValidationError("No se encontró el impuesto correspondiente a la unidad de medida " + str(uom_id.name) + " dentro de la configuración especial de IEPS.")

					amount = tax_ieps_id.amount * product_qty

					if tax_ieps_id:
						new_ieps_account_id = tax_ieps_id.invoice_repartition_line_ids.filtered(lambda i: i.account_id.name and 'IEPS' in i.account_id.name)
						ieps = move.line_ids.filtered(lambda i: i.name and 'IEPS' in i.name and i.debit > 0)
						amount = ieps.debit/0.16
						#_logger.info("---> amount: " + str(amount))
						line_ids.append({
									'account_id':new_ieps_account_id.account_id.id,
									'name': new_ieps_account_id.account_id.name,
									'move_id': self.id,
									'partner_id': line.partner_id.id,
									'company_id': line.company_id.id,
									'company_currency_id': line.company_currency_id.id,
									'quantity': 1.0,
									'date_maturity': False,
									'credit': amount,
									'exclude_from_invoice_tab': True,
									})

					line_ids.append({
							'account_id':line.account_id.id,
							'name': line.account_id.name,
							'move_id': self.id,
							'partner_id': line.partner_id.id,
							'company_id': line.company_id.id,
							'company_currency_id': line.company_currency_id.id,
							'quantity': 1.0,
							'date_maturity': False,
							'debit': amount,
							'exclude_from_invoice_tab': True,
							})
				else:
					if move.line_ids[1] and 'Pocari' in move.line_ids[1].name:
						line = move.line_ids[1]

					amount = 0
					tax_ieps_id = False
					itl_uom_tax_id = move.company_id.itl_uom_tax_ids.filtered(lambda i: uom_id.id == i.itl_uom_id.id)
					if not itl_uom_tax_id:
						raise ValidationError("No se encontró la unidad de medida " + str(uom_id.name) + " dentro de la configuración especial de IEPS.")

					tax_ieps_id = itl_uom_tax_id.itl_tax_id

					if not tax_ieps_id:
						raise ValidationError("No se encontró el impuesto correspondiente a la unidad de medida " + str(uom_id.name) + " dentro de la configuración especial de IEPS.")

					amount = tax_ieps_id.amount * product_qty

					if tax_ieps_id:
						new_ieps_account_id = tax_ieps_id.invoice_repartition_line_ids.filtered(lambda i: i.account_id.name and 'IEPS' in i.account_id.name)
						ieps = move.line_ids.filtered(lambda i: i.name and 'IEPS' in i.name and i.credit > 0)
						amount = ieps.credit/0.16
						line_ids.append({
								'account_id':new_ieps_account_id.account_id.id,
								'name': new_ieps_account_id.account_id.name,
								'move_id': self.id,
								'partner_id': line.partner_id.id,
								'company_id': line.company_id.id,
								'company_currency_id': line.company_currency_id.id,
								'quantity': 1.0,
								'date_maturity': False,
								'debit': amount,
								'exclude_from_invoice_tab': True,
									})

					line_ids.append({
								'account_id':line.account_id.id,
								'name': line.account_id.name,
								'move_id': self.id,
								'partner_id': line.partner_id.id,
								'company_id': line.company_id.id,
								'company_currency_id': line.company_currency_id.id,
								'quantity': 1.0,
								'date_maturity': False,
								'credit': amount,
								'exclude_from_invoice_tab': True,
								})
			return line_ids, tax_id

	def get_new_taxes(self):
		itl_transferred = []
		for line in self.invoice_line_ids:
			price = line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)
			taxes_line = line.filtered('price_subtotal').tax_ids.flatten_taxes_hierarchy()
			tax_line = {tax['id']: tax for tax in taxes_line.compute_all(price, line.currency_id, line.quantity, line.product_id, line.partner_id, is_refund=self.type in ('in_refund', 'out_refund'))['taxes']}
			transferred = taxes_line.filtered(lambda r: r.amount >= 0)
			for tax in transferred:
				vals = {}
				tax_dict = tax_line.get(tax.id, {})
				tasa = '%.6f' % abs(tax.amount if tax.amount_type == 'fixed' else (tax.amount / 100.0))
				tax_amount = '%.2f' % abs(tax_dict.get('amount', (tax.amount if tax.amount_type == 'fixed' else tax.amount / 100.0) * line.price_subtotal))
				vals['tax'] = tax
				vals['tax_dict'] = tax_dict
				vals['tasa'] = tasa
				vals['tax_amount'] = tax_amount
				itl_transferred.append(vals)
		return itl_transferred