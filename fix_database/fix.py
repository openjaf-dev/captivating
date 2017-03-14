# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _
from string import upper
from openerp.exceptions import except_orm, Warning, RedirectWarning

class fix_database(models.TransientModel):
    _name = 'fix.database'

    action = fields.Selection([('unique_partner', 'Unique Partner'), ('unique_product_hotel', 'Unique Product Hotel'), ], 'Action')
    product_hotel_id = fields.Many2one('product.hotel', 'Good Hotel',  ondelete="cascade")
    product_hotel_ids = fields.Many2many('product.hotel', 'fix_database_product_hotel_rel', 'fix_database_id', 'product_hotel_id', 'Bad Hotels',  ondelete="cascade")
    partner_id = fields.Many2one('res.partner', 'Good Partner',  ondelete="cascade")
    partner_ids = fields.Many2many('res.partner', 'fix_database_res_partner_rel', 'fix_database_id', 'partner_id', 'Bad Partner',  ondelete="cascade")

    @api.one
    @api.model
    def execute_action(self):
        res = getattr(self, self.action)()
        if self.action == 'unique_product_hotel' or self.action == 'unique_partner':
            view = self.env.ref('fix_database.fix_database_form')
            return {
                'name': _('Fix Database'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fix.database',
                'action': self.action,
                'target': 'new',
                'context': self._context,
                'views': [(view.id, 'form')],
            }
        return res

    @api.model
    def unique_partner(self):
        partner = self.env['res.partner']
        black_list = []
        try:
            bad_partner_id = partner.search([('name', 'ilike', upper(self.partner_id.name))]).ids
            good_partner_id = self.partner_id.id
        except:
            raise Warning(_('The name is not correct.'))

        if self.partner_ids:
            for part in self.partner_ids:
                if good_partner_id != part.id:
                    black_list.append(part.id)

        if bad_partner_id:
            black_list += bad_partner_id

        if good_partner_id in black_list:
                black_list.remove(good_partner_id)

        if black_list and good_partner_id:
            for p in black_list:
                self.env.cr.execute('update sale_order set partner_id=%s, partner_invoice_id=%s, partner_shipping_id=%s where partner_id=%s', (good_partner_id, good_partner_id, good_partner_id, p))
                self.env.cr.execute('update sale_order_line set customer_id=%s, order_partner_id=%s where customer_id=%s', (good_partner_id, good_partner_id, p))
                self.env.cr.execute('update sale_order_line set supplier_id=%s where supplier_id=%s', (good_partner_id, p))
                self.env.cr.execute('update account_voucher set partner_id=%s where partner_id=%s', (good_partner_id, p))
                self.env.cr.execute('update account_invoice set partner_id=%s, commercial_partner_id=%s where partner_id=%s', (good_partner_id, good_partner_id, p))
                self.env.cr.execute('update account_invoice_line set partner_id=%s where partner_id=%s', (good_partner_id, p))
                self.env.cr.execute('update account_move set partner_id=%s where partner_id=%s', (good_partner_id, p))
                self.env.cr.execute('update account_move_line set partner_id=%s where partner_id=%s', (good_partner_id, p))
                self.env.cr.execute('update account_model_line set partner_id=%s where partner_id=%s', (good_partner_id, p))
                self.env.cr.execute('update allotment_state set supplier_id=%s where supplier_id=%s', (good_partner_id, p))
                self.env.cr.execute('update payment_transaction set partner_id=%s where partner_id=%s', (good_partner_id, p))
                self.env.cr.execute('update product_pricelist_item set supplier_id=%s where supplier_id=%s', (good_partner_id, p))
                self.env.cr.execute('update res_partner_bank set partner_id=%s where partner_id=%s', (good_partner_id, p))
            for i in partner.browse(black_list):
                i.unlink()
        return True

    @api.multi
    def unique_product_hotel(self):
        product_hotel = self.env['product.hotel']
        product = self.env['product.product']
        try:
            bad_product_hotel_id = product_hotel.search([('hotel_name', 'ilike',
                                                          upper(self.product_hotel_id.name))]).ids
            good_product_id = self.product_hotel_id.product_id.id
            good_product_hotel_id = self.product_hotel_id.id
            good_product_template_id = self.product_hotel_id.product_id.product_tmpl_id.id
            good_product_name = self.product_hotel_id.product_id.name
            if good_product_hotel_id in bad_product_hotel_id:
                bad_product_hotel_id.remove(good_product_hotel_id)
        except:
            raise Warning(_('The name is not correct.'))

        black_list = []
        if self.product_hotel_ids:
            for bh in self.product_hotel_ids:
                if good_product_id != bh.product_id.id:
                    black_list.append((bh.product_id.id,
                                       bh.product_id.product_tmpl_id.uom_id.id,
                                       bh.product_id.product_tmpl_id.uos_id.id,
                                       bh.product_id.product_tmpl_id.id,
                                       bh.id))

        if bad_product_hotel_id:
            n = [v[0] for v in black_list]
            for bad in product_hotel.browse(bad_product_hotel_id):
                if bad.id not in n:
                    black_list.append((bad.product_id.id,
                                       bad.product_id.product_tmpl_id.uom_id.id,
                                       bad.product_id.product_tmpl_id.uos_id.id,
                                       bad.product_id.product_tmpl_id.id,
                                       bad.id))

        if not bad_product_hotel_id and not self.product_hotel_ids:
            raise Warning(_('The name is not duplicate.'))

        products = [(black_list,
                     good_product_id,
                     good_product_name,
                     good_product_template_id,
                     good_product_hotel_id)]
        for p in products:
            product_hotel_list = []
            product_list = []
            for x in p[0]:

                self.env.cr.execute('update sale_order_line set product_id=%s, product_uom=%s, product_uos=%s where product_id=%s', (p[1], x[1] or None, x[2] or None, x[0]))
                self.env.cr.execute('SELECT account_invoice.comment, account_invoice_line.name, account_invoice_line.invoice_id FROM '
                            'public.account_invoice, public.account_invoice_line WHERE '
                            'account_invoice.id = account_invoice_line.invoice_id AND account_invoice_line.product_id =%s', (x[0],))
                for (comment, name, invoice_id) in self.env.cr.fetchall():
                    description = 'Note:' + (comment or ' Change name product') + '. Change the line name product(' + name + ') by ' + p[2] + '.'
                    self.env.cr.execute('update account_invoice set comment=%s, name=%s where id=%s', (description, p[2], invoice_id))
                self.env.cr.execute('update account_invoice_line set product_id=%s, uos_id=%s where product_id=%s', (p[1], x[1] or None, x[0]))
                self.env.cr.execute('SELECT account_move.narration, account_move_line.name, account_move_line.move_id FROM '
                            'public.account_move, public.account_move_line WHERE '
                            'account_move.id = account_move_line.move_id AND account_move_line.product_id =%s', (x[0],))
                for (narration, name, move_id) in self.env.cr.fetchall():
                    description = 'Note:' + (narration or ' Change name product') + '. Change the line name product(' + name + ') by ' + p[2] + '.'
                    self.env.cr.execute('update account_move set narration=%s where id=%s', (description, move_id))
                self.env.cr.execute('update account_move_line set product_id=%s, product_uom_id=%s, name=%s where product_id=%s', (p[1], x[1] or None, p[2], x[0]))
                self.env.cr.execute('update account_analytic_line set product_id=%s, product_uom_id=%s where product_id=%s', (p[1], x[1] or None, x[0]))
                self.env.cr.execute('update product_pricelist_item set product_id=%s, product_tmpl_id=%s where product_id=%s and product_tmpl_id=%s', (p[1], p[3], x[0], x[3]))
                self.env.cr.execute('update product_supplierinfo set product_tmpl_id=%s where product_tmpl_id=%s', (p[3], x[3]))
                self.env.cr.execute('update sale_advance_payment_inv set product_id=%s where product_id=%s', (p[1], x[0]))
                self.env.cr.execute('update product_attribute_price set product_tmpl_id=%s where product_tmpl_id=%s', (p[3], x[3]))
                self.env.cr.execute('update product_attribute_line set product_tmpl_id=%s where product_tmpl_id=%s', (p[3], x[3]))
                self.env.cr.execute('update allotment_state set hotel_id=%s where hotel_id=%s', (p[4], x[4]))
                product_hotel_list.append(product_hotel.browse(x[4]))
                product_list.append(product.browse(x[0]))

            for prod_hotel in product_hotel_list:
                prod_hotel.unlink()
            for prod in product_list:
                prod.unlink()
        return True
