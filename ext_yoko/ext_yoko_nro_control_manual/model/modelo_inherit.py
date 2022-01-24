# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class AccountMove(models.Model):
    _inherit = 'account.move'

    def funcion_numeracion_fac(self):
        if self.type=="in_invoice":
            busca_correlativos = self.env['account.move'].search([('invoice_number','=',self.invoice_number_pro),('id','!=',self.id),('partner_id','=',self.partner_id.id)])
            for det_corr in busca_correlativos:
                if det_corr.invoice_number:
                    raise UserError(_(' El valor :%s ya se uso en otro documento')%det_corr.invoice_number)

            busca_correlativos2 = self.env['account.move'].search([('invoice_ctrl_number','=',self.invoice_ctrl_number_pro),('id','!=',self.id),('partner_id','=',self.partner_id.id)])
            for det_corr2 in busca_correlativos2:
                if det_corr2.invoice_ctrl_number:
                    raise UserError(_(' El nro de control TT  :%s ya se uso en otro documento')%det_corr2.invoice_ctrl_number)
            
            self.invoice_number=self.invoice_number_pro
            self.invoice_ctrl_number=self.invoice_ctrl_number_pro
            partners='pro' # aqui si es un proveedor

        if self.type=="in_refund" or self.type=="in_receipt":
            busca_correlativos = self.env['account.move'].search([('invoice_number','=',self.refuld_number_pro),('id','!=',self.id)])
            for det_corr in busca_correlativos:
                if det_corr.invoice_number:
                    raise UserError(_(' El valor :%s ya se uso en otro documento')%det_corr.invoice_number)

            busca_correlativos2 = self.env['account.move'].search([('invoice_ctrl_number','=',self.refund_ctrl_number_pro),('id','!=',self.id)])
            for det_corr2 in busca_correlativos2:
                if det_corr2.invoice_ctrl_number:
                    raise UserError(_(' El nro de control :%s ya se uso en otro documento')%det_corr2.invoice_ctrl_number)
                    
            self.invoice_number=self.refuld_number_pro
            self.invoice_ctrl_number=self.refund_ctrl_number_pro
            partners='cli' # aqui si es un cliente

        if self.type=="out_invoice":
            if self.nr_manual==False:
                self.invoice_number_cli=self.get_invoice_number_cli()
                self.invoice_number=self.invoice_number_cli #self.get_invoice_number_cli()
                self.invoice_ctrl_number=self.invoice_ctrl_number_cli
            else:
                self.invoice_number=self.invoice_number_cli
                self.invoice_ctrl_number=self.invoice_ctrl_number_cli

        if self.type=="out_refund":
            if self.nr_manual==False:
                self.refuld_number_cli=self.get_refuld_number_cli()
                self.invoice_number=self.refuld_number_cli #self.get_refuld_number_cli()
                self.invoice_ctrl_number=self.refund_ctrl_number_cli
            else:
                self.invoice_number=self.refuld_number_cli
                self.invoice_ctrl_number=self.refund_ctrl_number_cli

        if self.type=="out_receipt":
            if self.nr_manual==False:
                self.refuld_number_cli=self.get_refuld_number_pro()
                self.invoice_number=self.refuld_number_cli #self.get_refuld_number_cli()
                self.invoice_ctrl_number=self.refund_ctrl_number_cli
            else:
                self.invoice_number=self.refuld_number_cli
                self.invoice_ctrl_number=self.refund_ctrl_number_cli