from django.utils.encoding import smart_str
from ralph.discovery.models import DiskShare
import xlrd
workbook = xlrd.open_workbook('/home/kula/Downloads/storage_2014_06.xlsx')
with open('3par_2014_06_verified.txt', 'a+') as f:
    for name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(name)
        for i in xrange(sheet.nrows):
            current_row = sheet.row_values(i)
            try:
                DiskShare.objects.get(label=current_row[0])
                f.write(smart_str('{0};{1}\n'.format(current_row[0],1)))
            except DiskShare.MultipleObjectsReturned:
                diskshare = DiskShare.objects.filter(label=current_row[0])
                for i in diskshare:
                    f.write('{0};{1}\n'.format(current_row[0].encode('ascii', 'ignore'),1))
            except DiskShare.DoesNotExist:
                f.write(smart_str('{0};{1}\n'.format(current_row[0].encode('ascii', 'ignore'),0)))
