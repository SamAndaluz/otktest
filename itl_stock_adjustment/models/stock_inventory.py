from datetime import datetime, time, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import pytz


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory']

    selected_internal_locations = fields.Boolean(
        string="Internal location", default=True, states={'draft': [('readonly', False)]}, readonly=True,
        help="If is checked and set/clear widget is on then this type of locations will be added to location_ids.")
    selected_transit_locations = fields.Boolean(
        string="Transit location", default=True, states={'draft': [('readonly', False)]}, readonly=True,
        help="If is checked and set/clear widget is on then this type of locations will be added to location_ids.")
    bypass_exception = fields.Boolean(
        string="Bypass exception", default=False,
        help="When the widget is on then we can bypass the validate inventory button.")
    filling_inventory_deadline = fields.Datetime(
        compute="_setup_deadline", store=True, readonly=True,
        string="Dead line to fill the report", states={'draft': [('readonly', False)]},
        help="This method indicates the deadline to fill the report.")

    can_validate = fields.Boolean(
        compute="_can_validate", string="Can be validate", default=False, readonly=True,
        help="This field indicates if an inventory can be validate."
    )
    filling_report_ids = fields.One2many(
        'stock.inventory.filling.report', 'inventory_id', store=True,
        string="Filling report", compute="_update_filling_table"
    )
    has_warehouse_lines = fields.Boolean(
        compute="_has_line_warehouse", string="Has warehouse lines",
        help="Indicates if inventory has related inventory lines with warehouse in charge of given user.")
    has_confirmed = fields.Boolean(
        default=False, compute="_has_confirmed",
        string="Has confirmed", help="Indicates if the report has been reported."
    )
    completed = fields.Char(
        string="Status", store=False, default="Completed",
        help="Auxiliary field label to indicate inventory completed.")

    def _has_confirmed(self):
        for record in self:
            user_related_warehouses = list(record.get_related_warehouses().ids)
            record.has_confirmed = bool(record.filling_report_ids.search(
                ['&', '&',
                 ('inventory_id', '=', record.id),
                 ('warehouse_id', 'in', user_related_warehouses),
                 ('finished_at', '!=', False)]))

    def _has_line_warehouse(self):
        for record in self:
            location_ids = record.line_ids.search([('inventory_id', '=', record.id)]).location_id
            all_warehouses = record.get_warehouse_from_location(location_ids)
            user_related_warehouses = record.get_related_warehouses()
            record.has_warehouse_lines = bool(all_warehouses & user_related_warehouses)

    def get_related_warehouses(self):
        recordset = self.env['stock.warehouse']
        partner = self.env.user.partner_id
        if partner:
            return self.env['stock.warehouse'].sudo().search([('itl_encargado', '=', partner.id)])
        return recordset

    def add_locations(self):
        """
        Add locations to location_ids field which match with the given configuration
        (internal, in transit locations).
        :return: True
        """
        self.ensure_one()
        # relate all locations on selected_internal_locations (using locations flags)
        domain = []
        if self.selected_internal_locations:
            domain.append('internal')

        if self.selected_transit_locations:
            domain.append('transit')

        ids = self.env['stock.location'].search([('usage', 'in', domain)]).ids
        self.location_ids = [(6, 0, ids)]
        return True

    def clear_locations(self):
        """
        This method clears all locations on location_ids field.
        :return: True
        """
        self.ensure_one()
        # unlink all locations from selected_internal_locations
        self.location_ids = [(5, 0, 0)]
        return True

    @api.model
    def get_email_to(self):
        """
        We extract emails for the members of warehouse owner group.
        :return: (str) email formatted delimited by , (semicolon).
        """
        # TODO (jovani.martinez): to avoid hardcoding we must create a section on
        # inventory settings and we must add support for adding multiple groups
        # for r in report_receivers:
        user_group = self.env.ref("itl_stock_adjustment.group_warehouse_owners")  # i)
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.depends('state')
    def _setup_deadline(self):
        """
        We setup a deadline according with requirements to next day at noon if not
        dead line was specified.
        """
        for record in self:
            # If not deadline modified then we automatically setup to tomorrow noon.
            user_tz = record.create_uid.tz or pytz.UTC.zone
            local_tz = pytz.timezone(user_tz)

            if record.state == "confirm" and not record.filling_inventory_deadline:
                tomorrow = datetime.now(local_tz).date() + timedelta(days=1)
                noon = time(12, 0, 0)
                tomorrow_noon = datetime.combine(tomorrow, noon)
                # converting time zone aware to always set the deadline to user whom create the inventory
                local_time = local_tz.localize(tomorrow_noon)
                # due Odoo don't require timezone we just remove tz information
                record.filling_inventory_deadline = pytz.utc.normalize(local_time).replace(tzinfo=None)

    @api.depends('bypass_exception', 'line_ids')
    def _can_validate(self):
        """
        Check if we can proceed validating the inventory adjustment.
        :return: (bool) True if we can validate inventory or False otherwise.
        """
        for record in self:
            #  here we check if all inventory lines has been filled or needs to be filled.
            all_filled = all([l.was_filled for l in record.line_ids])
            if self.bypass_exception or all_filled:
                self.can_validate = True
            else:
                self.can_validate = False

    def action_validate(self):
        """
        (Override) Check if can proceeded validating inventory adjustment and then launch override action_validate.
        Otherwise raise validation error.
        """
        if not self.can_validate:
            raise ValidationError(
                'Some inventory lines need to be filled, you could bypass this turning on the bypass button.')
        super(StockInventory, self).action_validate()

    def get_action_from_name(self):
        """
        Get the id for the inventory form action. TODO (jovani.martinez): make this general.
        :return: id of the requested action.
        """
        results = self.env.ref('itl_stock_adjustment.action_inventory_form_inherit').read()
        if results:
            return results[0]['id']
        raise ValidationError("Error parsing the action from ref.")

    # TODO (jovani.martinez): this must be saved in a general utils module.
    def get_url(self, id=None, action=None, model=None, view_type=None):
        """
        This method returns the build url to access a field in a view on odoo.
        :param id: id of the record of interest.
        :param action: id of the action to be called.
        :param model: name of the model of the requested object.
        :param view_type: type of view to call (form|tree|kanban, etc.)
        :return: (str) with the formatted url ready to use.
        """
        base_url = "{}/web#".format(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        )
        assert action, "url needs an action."
        assert model, "url needs an model."
        assert view_type, "url needs an view_type."

        action = "action={}&".format(action)
        model = "model={}&".format(model)
        view_type = "view_type={}".format(view_type)

        build_url = action + model + view_type
        # no id indicates list view instead single view (kanban, list, pivot, etc.)
        if id:
            build_url = "id={}&".format(id) + build_url
        return base_url + build_url

    @api.depends('line_ids.location_id', 'line_ids.was_filled')
    def _update_filling_table(self):
        """
        Here we extracts all related warehouses for the given stock.inventory.lines, and also
        here we check if all lines related for a single warehouse were filled and the date of
        filling if any.
        """
        for record in self:
            # get no repeated locations related to lines.
            filled_related_location_ids = record.line_ids.search(
                [('inventory_id', '=', record.id), ('was_filled', '=', True)]).location_id
            unfilled_related_location_ids = record.line_ids.search(
                [('inventory_id', '=', record.id), ('was_filled', '=', False)]).location_id

            creation_records = []  # unlink all related warehouses first
            if record.filling_report_ids:
                # remove relations from db when unlink.
                for i in list(record.filling_report_ids.ids):
                    creation_records.append((2, i, 0))
            # get warehouses related to given locations
            warehouses = self.get_warehouse_from_location(
                filled_related_location_ids | unfilled_related_location_ids)
            for w in warehouses:
                # TODO (jovani.martinez): This will work on transit locations?
                filled_report_template = (0, 0, {"warehouse_id": w.id, "inventory_id": record.id})
                # intersect operations help us to find if some records are unfilled yet for any location.
                if not self.get_internal_stock_locations(w.lot_stock_id) & unfilled_related_location_ids:
                    # set the most recent date to take it as the finished filling date
                    filled_report_template[2]["finished_at"] = record.line_ids.search(
                        [('location_id', '=', w.lot_stock_id.id)], order="write_date desc", limit=1).write_date
                creation_records.append(filled_report_template)
            record.filling_report_ids = creation_records

    def get_internal_stock_locations(self, location):
        """
        Get all the children locations for a given locations
        (Note: the passed location is returned in the response also.)
        :param location: single stock.location record to extract all children locations.
        :return: return a recordset of children locations including passed location.
        """
        locations = self.env["stock.location"]
        if location.child_ids:
            for l in location.child_ids:
                locations |= self.get_internal_stock_locations(l)
        locations |= location
        return locations

    def get_warehouse_from_location(self, location_ids):
        """
        Get not repeated warehouses for given locations (if locations correspond to the
        same warehouse then just one warehouse is returned for that locations).
        :param location_ids: recordset of stock.location to extract the related warehouse.
        :return: return a recordset of the related stock.warehouse.
        """
        warehouses = self.env['stock.warehouse']
        for l in location_ids:
            warehouses |= l.sudo().get_warehouse()
        return warehouses

    def action_open_inventory_lines(self):
        """
        This method originally is used to show tree view of inventory lines, but here we added pivot view.
        """
        response = super(StockInventory, self).action_open_inventory_lines()
        response['views'] = [
            (self.env.ref("itl_stock_adjustment.view_inventory_line_custom_tree").id, "tree"),
            (self.env.ref("itl_stock_adjustment.view_inventory_line_pivot").id, "pivot")
        ]
        return response


class FillingReport(models.Model):
    _name = "stock.inventory.filling.report"

    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse",
        help="This field is related to a warehouse.")
    finished_at = fields.Datetime(
        string="Finished at",
        help="This field help us to check when a reported was completely finished."
    )
    updated = fields.Char(compute="_check_update", size=30, default='Not yet', string="Updated")
    inventory_id = fields.Many2one(
        "stock.inventory", string="Related inventory",
        help="This field is the related inventory."
    )

    @api.depends('finished_at')
    def _check_update(self):
        """
        This method is used to update the updated field with time of filling or not yet if
        not all warehouses inventory line are filled.
        """
        for record in self:
            if record.finished_at:
                record.updated = record.finished_at.isoformat()
            else:
                record.updated = "Not yet."
