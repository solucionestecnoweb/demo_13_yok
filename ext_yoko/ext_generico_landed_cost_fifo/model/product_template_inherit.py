# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price_div=fields.Float()
    tasa_compra=fields.Float()
    standard_price_div_fob=fields.Float()
    standard_price_fob=fields.Float()