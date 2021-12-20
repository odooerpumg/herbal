from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError,ValidationError
import os
import re
import xlrd
import urllib
from xlrd import open_workbook
from datetime import datetime,timedelta
import base64
import requests
import logging
from io import StringIO
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

header_fields = ['badge_id', 'date', 'amount', 'reason']


class DataImportAttendance(models.Model):
    _name = "dataimport.product"
    _description = 'Product Import'
    _order = 'id DESC'

    name = fields.Char('Description')
    import_date = fields.Date('Import Date', default=fields.Date.today)
    import_fname = fields.Char('Filename', size=128)
    import_file = fields.Binary('File', required=True)
    note = fields.Text('Log')
    
    
    
    def get_default_image(self, image):
        image_value = tools.image_resize_image_big(open(image, 'rb').read().encode('base64').strip())
        # image_value = image_value.replace('==', '')
        return image_value

    def get_image_from_url(self,image_url):
        """This method mainly use to get image from the url"""
        image = False
        if image_url:
            if "http://" in image_url or "https://" in image_url:
                image = base64.b64encode(requests.get(image_url).content)
            else:
                if 'file:' in image_url:
                    with open(image_url.split("file:///")[1], 'rb') as file:
                        image = base64.b64encode(file.read())
                if '/home' in image_url:
                    with open(image_url, 'rb') as file:
                        image = base64.b64encode(file.read())
            return image
     
    @api.onchange('import_fname')
    def onchange_import_fname(self):
        if self.import_fname:
            # Check Heading
            p, ext = os.path.splitext(self.import_fname)
            if ext:
                ext_name = ext.split('.')[1]
                if ext_name.lower() not in ('xls', 'xlsx'):
                    raise UserError(_("Please import EXCEL file!"))
            else:
                raise UserError(_("Please import EXCEL file!"))
    def float_hour_time(self, fh):
        h, r = divmod(fh, 1)
        m, r = divmod(r*60, 1)
        return (
            int(h),
            int(m),
            int(r*60),
        )
 
    def import_data(self):
        product_obj = self.env['product.template']
        log_msg = ''
        import_file =self.import_file
        lines = base64.decodestring(self.import_file)
        wb = xlrd.open_workbook(file_contents=lines)
        sheet = wb.sheet_by_index(0)
        badge_idx = date_idx = amount_idx = reason_idx = None
        deduction_data = []
        success_rows = []
 
        if sheet.nrows < 2:
            raise UserError(_("There is no line to import"))
 
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            if rowx > 1:
                value = {}
#                 if row[0].value:
                bu_br = row[0].value
                deaprt_id = row[1].value
                short_code = row[2].value
                location = row[3].value
                asset_name = row[4].value
                brand = row[5].value
                p_type = row[6].value
                user_name = row[7].value
                qr = row[8].value
                asset_type = row[9].value
                if len(row) > 10:
                    new_old = row[10].value
                if len(row)>11:
                    purchase_date =  row[11].value
                if len(row)>12:
                    image_medium = row[12].value
                    if image_medium:
                        image = self.get_image_from_url(image_medium)
                        value['image_1920'] = image
                bu_obj = self.env['hr.business']
                bu_br_obj = bu_obj.search([('name', '=', bu_br)])
                if not bu_br_obj:
                    bu = bu_br_obj.create({'name':bu_br})
                    value['bu_br_id'] = bu.id
                else:
                    value['bu_br_id'] = bu_br_obj[0].id
                
                depart_ob = self.env['hr.department']
                depart_obj = depart_ob.search([('name', '=', deaprt_id)])
                if not depart_obj:
                    deaprt_id = depart_ob.create({'name':deaprt_id})
                    value['department_id'] = deaprt_id.id
                else:
                    value['department_id'] = depart_obj[0].id
                
                
                product_ob = self.env['stock.location']
                if not short_code:
                    product_objs = product_ob.search([('name', '=', location)])
                    if not product_objs:
                       raise ValidationError('No location found with name '+location+'.')
                    else:
                        value['product_location_id'] = product_objs[0].id    
                else:
                    parent_id = product_ob.search([('name', '=', short_code),('usage','=','view')])
                    if not parent_id:
                        raise ValidationError('Parent Code is Wrong')
                    else:
                        stock_id = product_ob.search([('name', '=', location),('location_id','=',parent_id.id)])
                        if not stock_id:
                            raise ValidationError('No location found with name '+location+'.')
                        else:
                            value['product_location_id'] = stock_id[0].id                   
                brand_ob = self.env['product.brand']
                brand_objs = brand_ob.search([('name', '=', brand)])
                if not brand_objs:
                    ban_id = brand_ob.create({'name':brand})
                    value['brand_id'] = ban_id.id
                else:
                    value['brand_id'] = brand_objs[0].id
                
                pt_ob = self.env['product.type']
                pt_obj = pt_ob.search([('name', '=', p_type)])
                if not pt_obj:
                    pt_id = pt_ob.create({'name':p_type})
                    value['type_id'] = pt_id.id
                else:
                    value['type_id'] = pt_obj[0].id
                
                
                resp_ob = self.env['res.partner']
                resp_obj = resp_ob.search([('name', '=', user_name)], limit=1)
                if not resp_obj:
                    resp_id = resp_ob.create({'name':user_name})
                    value['user_type'] = resp_id.id
                else:
                    value['user_type'] = resp_obj[0].id
                
                
                value['name'] = asset_name
                value['default_code'] = qr

                type_obj = self.env['asset.types']
                type_ids = type_obj.search([('name', '=', asset_type)])
                if not type_ids:
                    bu = type_ids.create({'name':asset_type})
                    value['ga_it_id'] = bu.id
                else:
                    value['ga_it_id'] = type_ids[0].id
                if new_old:
                    value['new_old'] = new_old.lower()
                if purchase_date:
                    excel_date = purchase_date
                    excel_date = float(excel_date)
                    dt_2 = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(excel_date) - 2)
                    hour, minute, second = self.float_hour_time(excel_date % 1)
                    value['purchase_date'] = dt_2.replace(hour=hour, minute=minute, second=second)
                value['row_no'] = rowx
                value['type'] = 'product'
                deduction_data.append(value)
 
        for ded in deduction_data:
            row_no = ded['row_no']
            ded.pop('row_no', None)
            product_id = product_obj.search([('default_code','=',ded['default_code'])])
            if product_id:
                product_id.write(ded)
            else:
                product_obj.create(ded)
            # product_obj.create(ded)
            success_rows.append(row_no)
  
        if success_rows:
            success_msg = 'Row Numbers - %s are successfully imported!\n' % str(success_rows)
            log_msg = success_msg + log_msg
  
        self.write({'note': log_msg})