most_common_endings = [
        'GmbH & Co. Kommanditgesellschaft auf Aktien',
        'GmbH & Co. KGaA',
        'AG & Co. KGaA',
        'Aktiengeselschaft',
        'SA',
        'S.A.',
        'AG',
        'Ag',
        'ag',
        'SE',
        'S.E.',
        'plc',
        'Plc',
        'PLC',
        'GmbH',
        'KGaA',
        'Corp.',
        'Co.',
        'Inc.',
        '(Class C)',
        '(Class B)',
        '(Class A)',
        '(A)',
        '(B)',
        '(C)',
        'OJSC',
        'PJSC',
        'S.p.A.',
        'Oyj',
        '(Unternehmen)',
        '(Company)',
    ]

blocklist_search = ['SDAX', 'MDAX', 'TecDAX', 'S&P 500']


def remove_most_common_endings(company):
    for end in most_common_endings:
        company = company.replace(f' {end}', '')
    return company.replace(',', '')
