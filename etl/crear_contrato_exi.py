import pandas as pd

###################################################################
data_contract_success = {
    'commerce_id': ['KaSn-4LHo-m6vC-I4PU',
                        'Rh2k-J1o7-zndZ-cOo8',
                        'Vj9W-c4Pm-ja0X-fC1C',
                        'Vj9W-c4Pm-ja0X-fC1C',
                        'Vj9W-c4Pm-ja0X-fC1C',
                        '3VYd-4lzT-mTC3-DQN5',
                        '3VYd-4lzT-mTC3-DQN5',
                        'GdEQ-MGb7-LXHa-y6cd'],

    'commerce_name': ['Innovexa Solutions',
                        'QuantumLeap Inc',
                        'NexaTech Industries',
                        'NexaTech Industries',
                        'NexaTech Industries',
                        'Zenith Corp',
                        'Zenith Corp',
                        'FusionWave Enterprises'],

    'price_success': [300, 600, 250, 200, 170, 250, 130, 300],
    'min_limit_success': [0, 0, 0, 10000, 20000, 0, 22000, 0],
    }

def crear_exitosos():
    df_contract_success = pd.DataFrame(data_contract_success)
    return df_contract_success
