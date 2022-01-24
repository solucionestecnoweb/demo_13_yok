# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class AccountMove(models.Model):
    _inherit = 'account.move'

    condicion=fields.Char()
    vendedor = fields.Char()

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	condicion = fields.Char()
	vendedor = fields.Char()
