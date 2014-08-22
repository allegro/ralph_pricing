from decimal import Decimal

PRICING_SERVICE_COSTS = {
    1: [
        {
            'cost': Decimal('1000'),
            'pricing_object_id': 1,
            'type_id': 1,
            '_children': [
                {'cost': Decimal('100'), 'pricing_object_id': 1, 'type_id': 2},
                {'cost': Decimal('200'), 'pricing_object_id': 1, 'type_id': 3},
                {'cost': Decimal('700'), 'pricing_object_id': 1, 'type_id': 4},
            ],
        },
        {
            'cost': Decimal('2000'),
            'pricing_object_id': 2,
            'type_id': 1,
            '_children': [
                {'cost': Decimal('600'), 'pricing_object_id': 2, 'type_id': 2},
                {'cost': Decimal('600'), 'pricing_object_id': 2, 'type_id': 3},
                {'cost': Decimal('800'), 'pricing_object_id': 2, 'type_id': 5},
            ],
        },
    ],
    2: [
        {
            'cost': Decimal('1200'),
            'pricing_object_id': 3,
            'type_id': 1,
            '_children': [
                {'cost': Decimal('700'), 'pricing_object_id': 3, 'type_id': 2},
                {'cost': Decimal('500'), 'pricing_object_id': 3, 'type_id': 3},
            ],
        },
        {
            'cost': Decimal('900'),
            'pricing_object_id': 4,
            'type_id': 1,
            '_children': [
                {'cost': Decimal('400'), 'pricing_object_id': 4, 'type_id': 2},
                {'cost': Decimal('300'), 'pricing_object_id': 4, 'type_id': 3},
                {'cost': Decimal('200'), 'pricing_object_id': 4, 'type_id': 4},
            ],
        },
        {
            'cost': Decimal('300'),
            'pricing_object_id': 4,
            'type_id': 6,
            '_children': [
                {'cost': Decimal('100'), 'pricing_object_id': 4, 'type_id': 2},
                {'cost': Decimal('200'), 'pricing_object_id': 4, 'type_id': 3},
            ],
        },
    ],
}
