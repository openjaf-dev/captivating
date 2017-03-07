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


class fix_database(models.TransientModel):
    _name = 'fix.database'

    action = fields.Selection([('unique_partner', 'Unique Partner'), ('unique_product_hotel', 'Unique Product Hotel'), ], 'Action')
    product_hotel_id = fields.Many2one('product.hotel', 'Good Hotel')
    product_hotel_ids = fields.Many2many('product.hotel', 'fix_database_product_hotel_rel', 'fix_database_id', 'product_hotel_id', 'Bad Hotels')
    partner_id = fields.Many2one('res.partner', 'Good Partner')
    partner_ids = fields.Many2many('res.partner', 'fix_database_res_partner_rel', 'fix_database_id', 'partner_id', 'Bad Partner')

    @api.one
    @api.model
    def execute_action(self):
        res = getattr(self, self.action)()
        if self.action == 'unique_product_hotel':
            context = {}
            return {
                'name': 'Fix Database',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fix.database',
                'action': 'unique_product_hotel',
                'target': 'new',
                'context': context,
            }
        return res

    @api.model
    def unique_partner(self):
        try:
            bad_partner_id = self.partner_ids
            good_partner_id = self.partner_id.id
        except:
            raise osv.except_osv('Error', 'The name is not correct.')
        if bad_partner_id and good_partner_id:
            for p in bad_partner_id:
                self.env.cr.execute('update sale_order set partner_id=%s, partner_invoice_id=%s, partner_shipping_id=%s where partner_id=%s', (p.id, p.id, p.id, good_partner_id))
                self.env.cr.execute('update sale_order_line set customer_id=%s, order_partner_id=%s where customer_id=%s', (p.id, p.id, good_partner_id))
                self.env.cr.execute('update account_invoice set partner_id=%s, commercial_partner_id=%s where partner_id=%s', (p.id, p.id, good_partner_id))
                self.env.cr.execute('update account_invoice_line set partner_id=%s where partner_id=%s', (p.id, good_partner_id))
                self.env.cr.execute('update account_move set partner_id=%s where partner_id=%s', (p.id, good_partner_id))
                self.env.cr.execute('update account_move_line set partner_id=%s where partner_id=%s', (p.id, good_partner_id))
                if good_partner_id != p.id:
                    p.unlink()
        return True
    #
    # @api.model
    # def unique_product_hotel(self, self.env.cr, uid, context=None):
    #     product = self.pool.get('product.product')
    #     product_hotel = self.pool.get('product.hotel')
    #     obj = context['object']
    #     try:
    #         bad_product_id = product.search(self.env.cr, uid, [('name', 'ilike', upper(obj.product_hotel_id.name))], context=context)
    #         good_product_id = obj.product_hotel_id.product_id.id
    #         good_product_name = obj.product_hotel_id.product_id.name
    #         if good_product_id in bad_product_id:
    #             bad_product_id.remove(good_product_id)
    #     except:
    #         raise osv.except_osv('Error', 'The name is not correct.')
    #
    #     black_list = []
    #     if obj.product_hotel_ids:
    #         for bh in obj.product_hotel_ids:
    #             if good_product_id != bh.product_id.id:
    #                 black_list.append((bh.product_id.id, bh.product_id.product_tmpl_id.uom_id.id,
    #                                    bh.product_id.product_tmpl_id.uos_id.id))
    #
    #     if bad_product_id:
    #         n = [v[0] for v in black_list]
    #         for bad in product.browse(self.env.cr, uid, bad_product_id, context):
    #             if bad.id not in n:
    #                 black_list.append((bad.id, bad.product_tmpl_id.uom_id.id, bad.product_tmpl_id.uos_id.id))
    #
    #     if not bad_product_id and not obj.product_hotel_ids:
    #         raise osv.except_osv('Error', 'The name is not duplicate.')
    #
    #     products = [(black_list, good_product_id, good_product_name)]
    #     for p in products:
    #         for x in p[0]:
    #
    #             self.env.cr.execute('update sale_order_line set product_id=%s, product_uom=%s, product_uos=%s where product_id=%s', (p[1], x[1] or None, x[2] or None, x[0]))
    #             self.env.cr.execute('SELECT account_invoice.comment, account_invoice_line.name, account_invoice_line.invoice_id FROM '
    #                         'public.account_invoice, public.account_invoice_line WHERE '
    #                         'account_invoice.id = account_invoice_line.invoice_id AND account_invoice_line.product_id =%s', (x[0],))
    #             for (comment, name, invoice_id) in self.env.cr.fetchall():
    #                 description = 'Note:' + (comment or ' Change name product') + '. Change the line name product(' + name + ') by ' + p[2] + '.'
    #                 self.env.cr.execute('update account_invoice set comment=%s, name=%s where id=%s', (description, p[2], invoice_id))
    #             self.env.cr.execute('update account_invoice_line set product_id=%s, uos_id=%s where product_id=%s', (p[1], x[1] or None, x[0]))
    #             self.env.cr.execute('SELECT account_move.narration, account_move_line.name, account_move_line.move_id FROM '
    #                         'public.account_move, public.account_move_line WHERE '
    #                         'account_move.id = account_move_line.move_id AND account_move_line.product_id =%s', (x[0],))
    #             for (narration, name, move_id) in self.env.cr.fetchall():
    #                 description = 'Note:' + (narration or ' Change name product') + '. Change the line name product(' + name + ') by ' + p[2] + '.'
    #                 self.env.cr.execute('update account_move set narration=%s where id=%s', (description, move_id))
    #             self.env.cr.execute('update account_move_line set product_id=%s, product_uom_id=%s, name=%s where product_id=%s', (p[1], x[1] or None, p[2], x[0]))
    #             self.env.cr.execute('update account_analytic_line set product_id=%s, product_uom_id=%s where product_id=%s', (p[1], x[1] or None, x[0]))
    #             self.env.cr.execute('update product_pricelist_item set product_id=%s where product_id=%s', (p[1], x[0]))
    #             self.env.cr.execute('update product_supplierinfo set product_id=%s where product_id=%s', (p[1], x[0]))
    #
    #         self.pool.get('product.hotel').unlink(self.env.cr, uid, [x[0] for x in p[0]], context)
    #         self.pool.get('product.product').unlink(self.env.cr, uid, [x[0] for x in p[0]], context)
    #         self.pool.get('product.template').unlink(self.env.cr, uid, [x[0] for x in p[0]], context)
    #     return True
