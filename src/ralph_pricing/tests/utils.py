from ralph_pricing.models import Device, Venture


def get_or_create_device(name='Default', device_id=0):
    return Device.objects.get_or_create(name=name, device_id=device_id)[0]


def get_or_create_venture(name='Default', venture_id=0):
    return Venture.objects.get_or_create(name=name, venture_id=venture_id)[0]
