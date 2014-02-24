simple_tenant_usage_data = [
    {
        u'total_volume_gb_usage': 480.0,
        u'total_memory_mb_usage': 393216.0,
        u'total_vcpus_usage': 192.0,
        u'start': u'2012-09-05 00:00:00',
        u'tenant_id': u'e638ade19b0de826ee1391ee8e84dd7e',
        u'stop': u'2012-09-06 00:00:00',
        u'total_hours': 48.0,
        u'total_local_gb_usage': 768.0,
        u'total_images_gb_usage': 199.3,
    },
    {
        u'total_volume_gb_usage': 28800.0,
        u'total_memory_mb_usage': 786432.0,
        u'total_vcpus_usage': 384.0,
        u'start': u'2012-09-05 00:00:00',
        u'tenant_id': u'c6b791dae6baa644a71bed1a71615f2d',
        u'stop': u'2012-09-06 00:00:00',
        u'total_hours': 96.0,
        u'total_local_gb_usage': 1536.0,
        u'total_images_gb_usage': 315.0,
    },
    {
        u'total_volume_gb_usage': 0,
        u'total_memory_mb_usage': 98304.0,
        u'total_vcpus_usage': 48.0,
        u'start': u'2012-09-05 00:00:00',
        u'tenant_id': u'8c9b6d8553c91ae6ad5023cfc1febb1c',
        u'stop': u'2012-09-06 00:00:00',
        u'total_hours': 48.0,
        u'total_images_gb_usage': 45.0,
        u'total_local_gb_usage': 216.0,
    }]
tenants_usages_data = {u'tenant_usages': simple_tenant_usage_data}
tenants_data = {u'tenants': [
    {
        u'enabled': True,
        u'name': u'test_venture1',
        u'id': u'e638ade19b0de826ee1391ee8e84dd7e',
        u'description': 'venture:test_venture1;',
    },
    {
        u'enabled': True,
        u'name': u'test_venture2',
        u'id': u'c6b791dae6baa644a71bed1a71615f2d',
        u'description': 'venture:test_venture2;',
    },
    {
        u'enabled': False,
        u'name': u'test_venture3',
        u'id': u'8c9b6d8553c91ae6ad5023cfc1febb1c',
        u'description': 'fake description;'
    }
]}
tenants = {
    'e638ade19b0de826ee1391ee8e84dd7e': 'test_venture1',
    'c6b791dae6baa644a71bed1a71615f2d': 'test_venture2'
}
