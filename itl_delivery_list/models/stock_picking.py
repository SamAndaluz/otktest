from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"
    
    
    # Inherit
    def button_validate(self):
        rec = super(Picking, self).button_validate()
        
        #raise ValidationError("Testing...............")
        return rec
    
