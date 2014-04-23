from ralph_assets.models import Asset, AssetModel, AssetCategory, AssetManufacturer
import xlrd

PRINT_NEW_MODEL = False
PRINT_NEW_CATEGORY = False
PRINT_NEW_MANUFACTURER = False
PRINT_ADDED_POWER_CONSUMPTION = False
PRINT_ADDED_COLLOCATION = False
PRINT_ADDED_COLLOCATION = False
PRINT_MIGRATE_ASSETS = False

def migrate(xlsx_file):
    workbook = xlrd.open_workbook(xlsx_file)
    print (workbook.sheet_names())
    sheet = workbook.sheet_by_name('asset_models')

    for i in xrange(sheet.nrows):
        current_row = sheet.row_values(i)
        if i:
            if current_row[5]:
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                print 'New Model: {0}'.format(current_row[1])
                print 'Corec count: {0}'.format(current_row[5])
                print 'test: {0}'.format(current_row[7])
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    '''
    new_asset_model, model_created = AssetModel.objects.get_or_create(
        name=current_row[1],
    )[0]

    if model_created and PRINT_NEW_MODEL:
        print ''

    if not new_asset_model.category and current_row[3]:
        new_asset_model.category =\
            AssetCategory.objects.get_or_create(
                name=current_row[3],
                type=2
            )[0]

    if not new_asset_model.manufacturer and current_row[2]:
        new_asset_model.manufacturer =\
            AssetManufacturer.objects.get_or_create(
                name=current_row[2],
            )[0]

    if current_row[7]:
        if not new_asset_model.power_consumption:
            new_asset_model.power_consumption = current_row[7]
        elif current_row[7] != new_asset_model.power_consumption:
            print 'ERROR: current power consumption {0} new power consumption {1}'.format(new_asset_model.power_consumption, current_row[7])

    if current_row[8]:
        if not new_asset_model.height_of_device:
            new_asset_model.height_of_device = current_row[8]
        elif current_row[8] != new_asset_model.height_of_device:
            print 'ERROR: current height of device {0} new height of device {1}'.format(new_asset_model.height_of_device, current_row[8])

    new_asset_model.save()
    try:
        old_asset_model = AssetModel.objects.get(
            name=current_row[0],
        )

        for asset in Asset.objects.filter(model=old_asset_model):
            asset.model = new_asset_model
            asset.save()
            print 'Asset: {0}, Old Model: {1}, New Model: {2}'.format(
                asset.id, old_asset_model.name, new_asset_model.name)
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    except AssetModel.DoesNotExist:
        print 'ERROR: Model {0} does not exist'.format(current_row[0])
    '''

migrate('/home/kula/Downloads/asset_models v.1.6.xlsx')
