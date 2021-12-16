import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class HrExpenseCustom(models.Model):
    _inherit = "hr.expense"
    
    # Add new filter: check if there are attachments to change status
    def action_submit_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without product."))
        # Attachments filter
        if any(expense.attachment_number == 0 for expense in self):
            raise UserError(_("You can not create report without attachment documents."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        return {
            'name': _('New Expense Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': todo.ids,
                'default_company_id': self.company_id.id,
                'default_employee_id': self[0].employee_id.id,
                'default_name': todo[0].name if len(todo) == 1 else ''
            }
        }

class HrExpenseSheetCustom(models.Model):
    _inherit = "hr.expense.sheet"
    
    approvals_number = fields.Integer(string="Approvals", tracking=True)
    user_checked = fields.Boolean(compute="_get_user_check", string="User check")
    
    # Add new filter: check if there are attachments to change status
    def action_submit_sheet(self):
        # Attachments filter
        if self.attachment_number == 0:
            raise UserError(_("You can not submit without attachment documents."))
        self.write({'state': 'submit'})
        self.activity_update()
        # Schedule activity
        user_id = False
        
        ICPSudo = self.env['ir.config_parameter'].sudo()
        approver_1 = ICPSudo.get_param('hr_expense_extended.approver_1') or False
        approver_2 = ICPSudo.get_param('hr_expense_extended.approver_2') or False
        activity_type_to_create = ICPSudo.get_param('hr_expense_extended.activity_type_to_create') or False
        note = ICPSudo.get_param('hr_expense_extended.note') or False
        
        user_approver_1 = self.env['res.users'].browse(int(approver_1))
        user_approver_2 = self.env['res.users'].browse(int(approver_2))
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create))
        
        if not approver_1:
            raise UserError("There is not Approver 1 configured.")
        if not approver_2:
            raise UserError("There is not Approver 2 configured.")
        if not activity_type_to_create:
            raise UserError("There is not Activity type configured.")
            
        if self.user_id.login == user_approver_1.login:
            user_id = self.env['res.users'].search([('login','=',user_approver_2.login)])[0].id
        else:
            user_id = self.env['res.users'].search([('login','=',user_approver_1.login)])[0].id
            
        
        activity = self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'date_deadline': fields.Date.today(),
            'summary': activity_type.name,
            'user_id': user_id,
            'note': note,
            'res_id': self.id,
            'res_model': self.env['ir.model']._get(self._name).name,
            'res_model_id': self.env['ir.model']._get(self._name).id,
        })
        #raise ValidationError(str(activity))
        activity.action_close_dialog()
    
    def approve_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve', 'user_id': responsible_id})
        self.activity_update()

    def approve_counting(self):
        self.approvals_number = self.approvals_number + 1
        user_id = self.env.user.id
        
        self.env['expense.sheet.check'].create({
            'user_id': user_id,
            'expense_sheet_id': self.id
        })
        self._get_user_check()
        
        activity = self.env['mail.activity'].search([('user_id','=', user_id),('res_id','=',self.id),('res_model_id','=',self.env['ir.model']._get(self._name).id)])
        
        if activity:
            activity._action_done()
        
        if self.approvals_number == 2:
            self.approve_expense_sheets()
            
    def _get_user_check(self):
        user_id = self.env.user.id
        esc = self.env['expense.sheet.check']
        result = esc.search([('user_id','=',user_id),('expense_sheet_id','=',self.id)])
        
        if result:
            self.user_checked = True
        else:
            self.user_checked = False
            
class ExpenseSheetCheck(models.Model):
    _name = "expense.sheet.check"
    _description = "Expense Sheet Check"
    
    user_id = fields.Many2one('res.users', string="User")
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense sheet")