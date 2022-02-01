from odoo import api, fields, models, tools, _
from xlrd import open_workbook
from odoo.tools.translate import _
import xlrd
import base64
import logging
from datetime import datetime
from decimal import Decimal
from odoo.fields import Char
from odoo.exceptions import UserError
# from pip.commands.show import print_results
_logger = logging.getLogger(__name__)
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

header_fields = ['point_of_sale','company_id','payment_methods_ids','operation_type_id','sales_journal_id']		


header_indexes = {}

class ProductImport(models.Model):
    _name = "master.import"

    name = fields.Char('Description', required=True)
    import_date = fields.Date('Import Date', readonly=True)
    import_fname = fields.Char('Filename', size=128, required=True)
    import_file = fields.Binary('File', required=True)
    note = fields.Text('Log')
    company_id = fields.Many2one('res.company', 'Company', required=False)
    state = fields.Selection([('draft', 'Draft'),('completed', 'Completed'),('error', 'Error'),], 'States', default='draft')

    err_log = ''
    total_record = 0
    
    def _check_file_extension(self):
        for import_file in self.browse(self.ids):
            return import_file.import_fname.lower().endswith('.xls')  or import_file.import_fname.lower().endswith('.xlsx')


    _constraints = [(_check_file_extension, "Please import microsoft excel (.xlsx or .xls) file!", ['import_fname'])]

    # ## Load excel data file
    def get_excel_datas(self, sheets):
        result = []
        for s in sheets:
            # # header row
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
                            
            result.append(headers)
            
            # # value rows
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                result.append(values)
            self.total_record = len(result) - 1
        return result

    def float_hour_time(self, fh):
        h, r = divmod(fh, 1)
        m, r = divmod(r*60, 1)
        return (
            int(h),
            int(m),
            int(r*60),
        )
    
    # ## Check excel row headers with header_fields and define header indexes for database fields
    def get_headers(self, line):
        print("line[0].strip().lower()",line[0].strip().lower())
        if line[0].strip() not in header_fields:
            error_message = ("Error while processing the header line %s.\
                     \n\nPlease check your Excel separator as well as the column header fields") % line
            raise UserError(_(error_message))
        else:
            # ## set header_fields to header_index with value -1
            for header in header_fields:
                header_indexes[header] = -1  
                     
            col_count = 0
            for ind in range(len(line)):
                if line[ind] == '':
                    col_count = ind
                    break
                elif ind == len(line) - 1:
                    col_count = ind + 1
                    break
            
            for i in range(col_count):                
                header = line[i].strip()
                if header not in header_fields:
                    self.err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % header
                else:
                    header_indexes[header] = i
                                
            for header in header_fields:
                if header_indexes[header] < 0:                    
                    self.err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % header
    
    def import_data(self):
        print('IMPORT DATA IMPOre-------------------------')
        import_file = self.import_file
        header_line = True
        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = self.get_excel_datas(wb.sheets())
        all_data = []
        value = {}
        name = pack_size = None
        tag_one = tag_two = None
        create_count = 0
        update_count = 0
        skipped_count = 0
        skipped_data = []
        for line in excel_rows:
            if not line or line and line[0] and line[0] in ['', '#']:
                continue
            if header_line:
                self.get_headers(line)
                header_line = False 

            elif line and line[0] and line[0] not in ['#', '']:
                import_vals = {}
                # ## Fill excel row data into list to import to database
                for header in header_fields:
                    import_vals[header] = line[header_indexes[header]]
                # print line
                all_data.append(import_vals)
       
        if self.err_log:
            import_id = self.ids[0]
            err = self.err_log
            #self.write(self.ids[0], {'note': ''})
            self.write({'note': err,'state': 'error'})
        else:
            for data in all_data:
                excel_row = all_data.index(data) + 2

                name=company_id=payment_methods_ids=picking_type_id=sales_journal_id=None
                print ('excel row => ' + str(all_data.index(data) + 2))
                print ('data ' + str(data))
                name = str(data['point_of_sale']).strip()
                company_id = int(str(data['company_id']).strip())
                
                # payment_methods_ids
                print("payment_methods_ids_str==>", data['payment_methods_ids'])
                payment_methods_ids_str = str(data['payment_methods_ids']).strip()
                
                payment_methods_ids = []
                for i in payment_methods_ids_str.split(","):
                    payment_methods_ids.append(int(float(i)))
                payment_methods = self.env['pos.payment.method'].search([("company_id","=",company_id)])
                print("payment_methods_ids",payment_methods_ids)
                # picking_type_id
                picking_type_id = int(float(str(data['operation_type_id'])))

                # sales_journal_id
                sales_journal_id = int(float(str(data['sales_journal_id']).strip()))

                inter_user = self.env['res.users'].browse(2)
                pos_config = self.env['pos.config']
                invoice_journal = self.env['account.journal'].search([("company_id","=",company_id),("code","=","INV"),("type","=","sale")])
                sale_journal = self.env['account.journal'].search([("company_id","=",company_id),("code","=","POSS"),("type","=","sale")])
                data = {
                    "name": name,
                    "company_id": company_id,
                    "payment_method_ids": payment_methods.ids,
                    "picking_type_id": picking_type_id,
                    "journal_id": sale_journal.id,
                    "invoice_journal_id": invoice_journal.id,
                }
                result = pos_config.with_context(allowed_company_ids=inter_user.company_ids.ids).create(data)
                create_count += 1

                skipped_data_str = ''
                for sk in skipped_data:
                    skipped_data_str += str(sk) + ','                
                message = 'Import Success at ' + str(datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                          '%Y-%m-%d %H:%M:%S'))+ '\n' + str(len(all_data))+' records imported' +'\
                          \n' + str(create_count) + ' created\n' + str(update_count) + ' updated' + '\
                          \n' + str(skipped_count) + 'skipped' + '\
                          \n\n' + skipped_data_str
                          
                self.write({'state': 'completed','note': message})
                



                
