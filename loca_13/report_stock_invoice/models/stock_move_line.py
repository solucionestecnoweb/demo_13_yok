# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_ids = fields.Many2many(compute="_compute_picking_invoice_ids", comodel_name="account.move",
                                    copy=False, string="Facturas", store=True)
    is_invoice = fields.Boolean(string="Tiene Factura", compute="_compute_picking_invoice_ids", store=True, default=False)

    @api.depends('sale_id.invoice_ids')
    def _compute_picking_invoice_ids(self):
        for picking in self:
            if picking.sale_id.invoice_ids:
                picking.invoice_ids = picking.sale_id.invoice_ids
                picking.is_invoice = True
            else:
                picking.is_invoice = False
                return ''


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    invoice_ids = fields.Many2many(compute="compute_invoice_and_delivery_note", comodel_name="account.move",
                                   copy=False, string="Facturas", store=True)
    doc_note_entrega = fields.Char(string="Nota de entrega", readonly=True, compute='compute_invoice_and_delivery_note',
                                   store=True)
    categ_id = fields.Many2one(related='product_id.categ_id', store=True)
    forma_id = fields.Many2one(related='product_id.forma_id', store=True)
    color_id = fields.Many2one(related='product_id.color', store=True)
    modelo_id = fields.Many2one(related='product_id.modelo_id', store=True)
    tipo_id = fields.Many2one(related='product_id.tipo_id', store=True)
    formato_id = fields.Many2one(related='product_id.formato', store=True)
    uso_id = fields.Many2one(related='product_id.uso', store=True)
    material_id = fields.Many2one(related='product_id.material', store=True)
    marca_comercial_id = fields.Many2one(related='product_id.marca_comercial', store=True)
    calidad_id = fields.Many2one(related='product_id.calidad', store=True)
    uni_neg_id = fields.Many2one(related='product_id.uni_neg_id', store=True)

    @api.depends(
        'picking_id.is_invoice',
        'picking_id.invoice_ids.correlativo_nota_entrega',
        'picking_id.invoice_ids.invoice_number_cli'
    )
    def compute_invoice_and_delivery_note(self):
        for line in self:
            picking_obj = line.env['stock.picking'].search([('id', '=', line.picking_id.id)])
            if picking_obj.invoice_ids:
                line.invoice_ids = picking_obj.invoice_ids
                for inv in picking_obj.invoice_ids:
                    if inv.correlativo_nota_entrega:
                        line.doc_note_entrega = inv.correlativo_nota_entrega

