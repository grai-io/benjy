import random
import datetime
import pandas as pd
import os
from functools import reduce
from math import prod
import uuid

time_intervals = ['seconds', 'minutes', 'hours', 'days', 'weeks'][::-1]
conversions = [1, 7, 24, 60, 60]  # week, day, hour, minute, second
measures = [prod(conversions[0:(n+1)]) for n in range(len(conversions))]

rand_range_intervals = dict(zip(time_intervals, measures))


def id_gen(prefix):
    def inner(n):
        return [f'{prefix}_{str(random.randint(0, 100))}' for i in range(n)]
    return inner


# valid intervals include [seconds, minutes, hours]
def timestamp_gen(interval, num_max_periods=1):
    start_date = datetime.datetime(2020, 1, 1, 0, 0, 0)
    rand_range = rand_range_intervals[interval] * num_max_periods

    def inner(n):
        deltas = (datetime.timedelta(**{interval: random.randint(0, rand_range)}) for i in range(n))
        return [start_date + delta for delta in deltas]

    return inner


def sales_gen(val_min, val_max):
    def inner(n):
        return [random.randint(val_min, val_max) for i in range(n)]
    return inner


n = 10000
params = {
    'a': {'id': id_gen('a'), 'ts': timestamp_gen('hours'), 'sales': sales_gen(1, 100)},
    'b': {'id': id_gen('b'), 'ts': timestamp_gen('hours'), 'sales': sales_gen(1, 100)},
    'c': {'id': id_gen('c'), 'ts': timestamp_gen('hours'), 'sales': sales_gen(1, 100)},
}

# Mock data
root_folder = 'project'
data_paths = {}
simmed_data = {}
for k, param in params.items():
    df = pd.DataFrame({k: v(n) for k, v in param.items()})
    df = df.groupby(['id', 'ts'], as_index=False)['sales'].sum().sort_values('ts', ascending=True)
    output_path = os.path.join(root_folder, 'data', f'sales_source_{k}_table.csv')
    data_paths[k] = output_path
    simmed_data[k] = df
    df.to_csv(output_path, index=False)


# Mock crosswalks
def id_getter(id_map, prob):
    ids = list(id_map.values())
    def inner():
        return uuid.uuid4() if random.random() > prob else random.choice(ids)
    return inner


id_gen = iter({k: df['id'].unique() for k, df in simmed_data.items()}.items())
is_cross_prob = .3

k, v = next(id_gen)
df = pd.DataFrame({'uuid': [uuid.uuid4() for _ in v], f'id_{k}': v})
id_map = dict(zip(df[f'id_{k}'], df['uuid']))
uuids = list(df['uuid'])
output_path = os.path.join(root_folder, 'data/crosswalks', f'crosswalk_uuid_{k}_table.csv')
df.to_csv(output_path, index=False)

for k, v in id_gen:
    get_id = id_getter(id_map, is_cross_prob)
    df = pd.DataFrame({'uuid': [get_id() for _ in v], f'id_{k}': v})
    id_map = dict(zip(df[f'id_{k}'], df['uuid']))
    output_path = os.path.join(root_folder, 'data/crosswalks', f'crosswalk_uuid_{k}_table.csv')
    df.to_csv(output_path, index=False)
    uuids += list(df['uuid'])

uuids = set(uuids)
df = pd.DataFrame({"uuid": list(uuids)})
output_path = os.path.join(root_folder, 'data', f'uuid_table.csv')
df.to_csv(output_path, index=False)


# Build Entities:

