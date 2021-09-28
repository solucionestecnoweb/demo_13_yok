from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import logging
from base64 import encodestring

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt
import xml.etree.ElementTree as ET

class Partners(models.Model):
    _inherit = 'account.journal'

    tipo_doc = fields.Selection([('nc', 'Nota de Credito'),('nb', 'Nota de Debito'),('fc','Factura'),('ne','Nota de Entrega')])

class AccountMove(models.Model):
    _inherit = 'account.move'

    date_actual = fields.Date(default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    act_nota_entre=fields.Boolean(default=False)
    correlativo_nota_entrega = fields.Char(required=False)
    doc_currency_id = fields.Many2one("res.currency", string="Moneda del documento Físico")
    currency_company_id = fields.Many2one("res.currency", string="Moneda de la compañia",default=lambda self: self.env.company.currency_id)
    condicion = fields.Char()
    vendedor = fields.Many2one("hr.employee",string="Vendedor")
    tipo_transporte=fields.Char()
    persona_contacto=fields.Char()

    def action_invoice_sent(self):
        if self.partner_id.email:
            template = self.env.ref('ext_yoko_formato_factura_nd_nc.email_template_fxo_send_email_fact', False)
            attachment_ids = []
            attach = {}
            result_pdf, type = self.env['ir.actions.report']._get_report_from_name('ext_yoko_formato_factura_nd_nc.report_invoice_with_payments_electronica').render_qweb_pdf(self.id)
            attach['name'] = 'Factura.pdf'
            attach['type'] = 'binary'
            attach['datas'] = encodestring(result_pdf)
            # attach['datas_fname'] = 'Comprobante de IVA.pdf'
            attach['res_model'] = 'mail.compose.message'
            attachment_id = self.env['ir.attachment'].create(attach)
            attachment_ids.append(attachment_id.id)

            mail = template.send_mail(self.id, force_send=True,email_values={'attachment_ids': attachment_ids}) #envia mail
            if mail:
                self.message_post(body=_("Enviado email al Cliente: %s"%self.partner_id.name))
                self.state_dte_partner = 'sent'
                print('Correo Enviado a '+ str(self.partner_id.email))


    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result = "0,00"
        return result

    def action_post(self):
        super().action_post()
        if self.act_nota_entre==True:
            if self.journal_id.tipo_doc=="ne":
                self.correlativo_nota_entrega=self.get_nro_nota_entrega()
            else:
                raise UserError(_('Diario no adecuado para la nota de entrega. Seleccione el diario correcto o vaya a configuracion->diario y en el campo tipo_doc coloque Nota de entrega"'))
        self.valida_fact_ref()

    def get_nro_nota_entrega(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_nro_control_nota_entrega'+str(self.company_id.id)
        company_id = self.company_id.id
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': '00-',
                'name': 'Localización Venezolana Nro control Nota entrega %s' % 1,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 4,
                'number_increment': 1,
                'company_id': company_id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        #self.refuld_number_pro=name
        return name

    def valida_fact_ref(self):
        if self.type=="out_refund" or self.type=="out_receipt":
            busca_fact= self.env['account.move'].search([('invoice_number','=',self.ref)])
            if not busca_fact:
                busca_fact2 = self.env['account.move'].search([('name','=',self.ref)])
                if busca_fact2:
                    for dett in busca_fact2:
                        self.ref=dett.invoice_number
                else:
                    raise UserError(_('La factura de referencia afectada introducida no coincide con una factura anterior o no existe'))

    def muestra_nota_entrega(self):
        valor=0
        if self.act_nota_entre==False:
            raise UserError(_('Este documento no esta activado como Nota de entrega. Por Favor active la opcion "Aplica Nota de Entrega?"'))
        else:
            valor=self.correlativo_nota_entrega
        return valor

    def formato_fecha(self,date):
        fecha = str(date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def doc_origen(self,valor):
        fecha_entrega=self.invoice_date
        busca_origen = self.env['sale.order'].search([('name','=',valor)])
        if busca_origen:
            for det in busca_origen:
                fecha_entrega=det.date_order
        return fecha_entrega

    def razon_dev(self):
        motivo="---"
        busca_razon = self.env['account.move.reversal'].search([('move_id','=',self.reversed_entry_id.id)])
        if busca_razon:
            for det in busca_razon:
                motivo=det.reason
        return motivo

    def base_imponible_fact_orig(self,fact_org):
        acum=0
        if self.reversed_entry_id.id:
            busca_original = self.env['account.move.line'].search([('move_id','=',self.reversed_entry_id.id)])
        else:
            busca_move= self.env['account.move'].search([('invoice_number','=',fact_org)])
            if busca_move:
                for rec in busca_move:
                    busca_original = self.env['account.move.line'].search([('move_id','=',rec.id)])
        if busca_original:
            for det in busca_original:
                if det.product_id.id and det.tax_ids.amount:
                    acum=acum+det.price_subtotal
        return acum

    def iva_fact_orig(self,fact_org):
        iva=0
        if self.reversed_entry_id.id:
            busca_original = self.env['account.move'].search([('id','=',self.reversed_entry_id.id)])
        else:
            busca_original = self.env['account.move'].search([('invoice_number','=',fact_org)])
        if busca_original:
            for det in busca_original:
                iva=det.amount_tax
        return iva

    def neto_fact_orig(self,fact_org):
        neto=0
        if self.reversed_entry_id.id:
            busca_original = self.env['account.move'].search([('id','=',self.reversed_entry_id.id)])
        else:
            busca_original = self.env['account.move'].search([('invoice_number','=',fact_org)])
        if busca_original:
            for det in busca_original:
                neto=det.amount_total
        return neto


    def doc_cedula(self,aux):
        #nro_doc=self.partner_id.vat
        busca_partner = self.env['res.partner'].search([('id','=',aux)])
        for det in busca_partner:
            tipo_doc=busca_partner.doc_type
            if busca_partner.vat:
                nro_doc=str(busca_partner.vat)
            else:
                nro_doc="00000000"
            tipo_doc=busca_partner.doc_type
        nro_doc=nro_doc.replace('V','')
        nro_doc=nro_doc.replace('v','')
        nro_doc=nro_doc.replace('E','')
        nro_doc=nro_doc.replace('e','')
        nro_doc=nro_doc.replace('G','')
        nro_doc=nro_doc.replace('g','')
        nro_doc=nro_doc.replace('J','')
        nro_doc=nro_doc.replace('j','')
        nro_doc=nro_doc.replace('P','')
        nro_doc=nro_doc.replace('p','')
        nro_doc=nro_doc.replace('-','')
        
        if tipo_doc=="v":
            tipo_doc="V"
        if tipo_doc=="e":
            tipo_doc="E"
        if tipo_doc=="g":
            tipo_doc="G"
        if tipo_doc=="j":
            tipo_doc="J"
        if tipo_doc=="p":
            tipo_doc="P"
        resultado=str(tipo_doc)+"-"+str(nro_doc)
        return resultado

    def fact_div(self,valor):
        self.currency_id.id
        fecha_contable_doc=self.date
        monto_factura=self.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if self.currency_id.id!=self.doc_currency_id.id:
            if self.currency_id!=self.company_id.currency_id.id:
                tasa= self.env['account.move'].search([('id','=',self.id)],order="id asc")
                for det_tasa in tasa:
                    monto_nativo=det_tasa.amount_untaxed_signed
                    monto_extran=det_tasa.amount_untaxed
                    valor_aux=abs(monto_nativo/monto_extran)
                rate=round(valor_aux,3)  # LANTA
                #rate=round(valor_aux,2)  # ODOO SH
                resultado=valor*rate
            else:
                resultado=valor
        else:
            resultado=valor
        return resultado
        
    def get_invoice_number_cli(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_factura_cliente'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id #loca 14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) #loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': 'FACT/',
                    'name': 'Localización Venezolana Factura cliente %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, #loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.invoice_number_cli=name
        """else:
            name='0'"""
        return name

    def get_invoice_ctrl_number_cli(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_control_factura_cliente'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id #loca 14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) # loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': '00-',
                    'name': 'Localización Venezolana nro control Factura cliente %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, #loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.invoice_number_cli=name
        """else:
            name='0'"""
        return name

    def get_refuld_number_cli(self):# nota de credito cliente
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_factura_nota_credito_cliente'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id # loca 14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) # loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': 'NCC/',
                    'name': 'Localización Venezolana Nota Credito Cliente %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, # loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.refuld_number_cli=name
        """else:
            name='0'"""
        return name

    def get_refuld_ctrl_number_cli(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:  
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_control_nota_credito_cliente'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id #loca 14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) #loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': '00-',
                    'name': 'Localización Venezolana nro control Nota Credito Cliente %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, #loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.refuld_number_cli=name
        """else:
            name='0'"""
        return name

    def get_refuld_number_pro(self): #nota de debito Cliente
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_factura_nota_debito_cliente'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id #loca14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) #loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': 'NDC/',
                    'name': 'Localización Venezolana Nota Debito Cliente %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, #loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.refuld_number_pro=name
        """else:
            name='0'"""
        return name

    def get_refuld_ctrl_number_pro(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_control_nota_debito_cliente'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id #loca 14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) #loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': '00-',
                    'name': 'Localización Venezolana Nro control Nota debito cliente %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, # loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.refuld_number_pro=name
        """else:
            name='0'"""
        return name

    def get_invoice_ctrl_number_unico(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_ve_cuenta_retencion_iva'''
        name=''
        if self.act_nota_entre==False:
            self.ensure_one()
            SEQUENCE_CODE = 'l10n_ve_nro_control_unico_formato_libre'+str(self.company_id.id) #loca 14
            company_id = self.company_id.id #loca 14
            IrSequence = self.env['ir.sequence'].with_context(force_company=company_id) #loca 14
            name = IrSequence.next_by_code(SEQUENCE_CODE)

            # si aún no existe una secuencia para esta empresa, cree una
            if not name:
                IrSequence.sudo().create({
                    'prefix': '00-',
                    'name': 'Localización Venezolana nro control Unico Factura Forma Libre %s' % 1,
                    'code': SEQUENCE_CODE,
                    'implementation': 'no_gap',
                    'padding': 4,
                    'number_increment': 1,
                    'company_id': company_id, #loca 14
                })
                name = IrSequence.next_by_code(SEQUENCE_CODE)
            #self.invoice_number_cli=name
        """else:
            name='0'"""
        return name

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def formato_fecha(self):
        fecha = str(self.invoice_id.invoice_date)
        fecha_aux=fecha
        ano=fecha_aux[0:4]
        mes=fecha[5:7]
        dia=fecha[8:10]  
        resultado=dia+"/"+mes+"/"+ano
        return resultado

    def float_format(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',','*')
            result = result.replace('.',',')
            result = result.replace('*','.')
        else:
            result = "0,00"
        return result

    def fact_div_line(self,valor):
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        if self.move_id.currency_id.id!=self.move_id.doc_currency_id.id:
            tasa= self.env['account.move'].search([('id','=',self.move_id.id)],order="id asc")
            for det_tasa in tasa:
                monto_nativo=det_tasa.amount_untaxed_signed
                monto_extran=det_tasa.amount_untaxed
                valor_aux=abs(monto_nativo/monto_extran)
            rate=round(valor_aux,3)  # LANTA
            #rate=round(valor_aux,2)  # ODOO SH
            resultado=valor*rate
        else:
            resultado=valor
        return resultado

