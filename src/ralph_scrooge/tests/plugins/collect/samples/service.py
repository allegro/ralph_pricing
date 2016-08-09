SAMPLE_SERVICES = [
    {
        'id': 123,
        'uid': 's-1',
        'name': 'Service #1',
        # 'business_line': 'bl-1',  # XXX ?
        'profit_center': {'id': 11},
        'business_owners': [
            {'id': 1, 'username': 'some_user_1'},
            {'id': 2, 'username': 'some_user_2'},
            {'id': 3, 'username': 'some_user_3'},
        ],
        'technical_owners': [
            {'id': 4, 'username': 'some_user_4'},
            {'id': 5, 'username': 'some_user_5'},
        ],
    },
    {
        'id': 322,
        'uid': 's-2',
        'name': 'Service #2',
        # 'business_line': 'bl-2',  # XXX ?
        'profit_center': {'id': 22},
        'business_owners': [
            {'id': 1, 'username': 'some_user_1'},
        ],
        'technical_owners': [
            {'id': 5, 'username': 'some_user_5'},
            {'id': 6, 'username': 'some_user_6'},
        ],
    },
]
