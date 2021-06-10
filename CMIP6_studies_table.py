import natsort as ns
import numpy as np
import pandas as pd
import YamlStudies as ys
import yaml

def synthesis(binvalues):
  return(np.logical_and.reduce(binvalues, 1)*1)

with open('CMIP6_studies_config.yaml') as fp:
  config = yaml.load(fp, Loader=yaml.FullLoader)

alldata = ys.load_from_files('CMIP6_studies/*.yaml', skip_disabled = False, skip_cause = 'incomplete')
alldata = [x for x in alldata if x.spatial_scope in config['spatial_scope_filter']['EUR']]

# Performance
tableperf = pd.concat([x.get_formatted_data() for x in alldata if x.type=='performance'], axis=1)

# Plausible range rows
tableprange= pd.concat(
  [x.get_plausible_values() for x in alldata if x.type in ('performance')],
  axis=1
)
tableprange.index = pd.MultiIndex.from_tuples(
  [('. Plausible values', idx) for idx in tableprange.index],
  names = ['model','run']
)

# Classes table (when available)
tableclass = pd.concat([x.get_class_data() for x in alldata], axis=1)
tableclass = tableclass.reindex(ns.natsorted(tableclass.index))

# Binary table
tablebin = pd.concat([x.get_plausible_mask() for x in alldata if x.type=='performance'], axis=1) * 1
# Add synthesis column
tableperf.insert(0, column='Synthesis', value=synthesis(tablebin.values))
tableprange = pd.concat([tableprange, tableperf])
# sort synthesis column first
synthfirst = list(tableprange.columns)
synthfirst.insert(0, synthfirst.pop(synthfirst.index('Synthesis')))
tableprange = tableprange.reindex(synthfirst, axis=1)

# Spread
tablespread = pd.concat(
  [x.get_formatted_data() for x in alldata if x.type=='future_spread'],
  axis=1
)

# Independence
tableindep = pd.concat(
  [x.data for x in alldata if x.type=='independence'],
  axis=1
)

# All together
tablefull = pd.concat([tableprange,tablespread, tableindep], axis=1, keys=['performance', 'spread', 'independence'])
tablefull = tablefull.reindex(ns.natsorted(tablefull.index))
# Dump final CSV
tablefull.to_csv(
  'CMIP6_studies_table.csv', float_format = '%.2f', index_label = ['model', 'run']
)
