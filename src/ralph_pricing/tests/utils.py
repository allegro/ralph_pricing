from ralph_pricing.models import DailyDevice, Device, Venture


def get_or_create_device(name='Default', device_id=0, asset_id=0, **kwargs):
    return Device.objects.get_or_create(
        name=name,
        device_id=device_id,
        asset_id=asset_id,
        **kwargs
    )[0]


def get_or_create_venture(name='Default', venture_id=0):
    return Venture.objects.get_or_create(name=name, venture_id=venture_id)[0]


def get_or_create_dailydevice(date, pricing_device, venture, **kwargs):
    return DailyDevice.objects.get_or_create(
        date=date,
        pricing_device=pricing_device,
        pricing_venture=venture,
        **kwargs
    )[0]
