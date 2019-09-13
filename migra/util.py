from __future__ import unicode_literals

from collections import OrderedDict as od

import re

def differences(a, b, add_dependencies_for_modifications=True, process=False, tables_only=False, target_schema=None):
    if process and tables_only:
        a, a_keys, a_old_keys = preprocess(a)
        b, b_keys, b_old_keys = preprocess(b)
        keys_added = set(b_keys) - set(a_keys)
        keys_removed = set(a_keys) - set(b_keys)
        keys_common = set(a_keys) & set(b_keys)
        added = od((k, b[k]) for k in sorted(keys_added))
        removed = od((k, a[k]) for k in sorted(keys_removed))
        modified = od((k, b[k]) for k in sorted(keys_common) if a[k] != b[k])
        unmodified = od((k, b[k]) for k in sorted(keys_common) if a[k] == b[k])
        # convert back
        #added = od((a_old_keys[k], added[k]) for k in sorted(added.keys()))
        modified = od((a_old_keys[k], modified[k]) for k in sorted(modified.keys()))
        removed = od((a_old_keys[k], removed[k]) for k in sorted(removed.keys()))
        #unmodified = od((a_old_keys[k], unmodified[k]) for k in sorted(unmodified.keys()))

    else:
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        keys_added = set(b_keys) - set(a_keys)
        keys_removed = set(a_keys) - set(b_keys)
        keys_common = set(a_keys) & set(b_keys)
        added = od((k, b[k]) for k in sorted(keys_added))
        removed = od((k, a[k]) for k in sorted(keys_removed))
        modified = od((k, b[k]) for k in sorted(keys_common) if a[k] != b[k])
        unmodified = od((k, b[k]) for k in sorted(keys_common) if a[k] == b[k])

    # check in added only to update schema names
    # for k in added:
    #     try: 
    #         if target_schema and added[k].is_table and added[k].schema != target_schema:
    #             added[k].schema = target_schema
    #     except AttributeError:
    #         continue
    if target_schema:
        added = update_schema(added, target_schema)
        removed = update_schema(removed, target_schema)
        modified = update_schema(modified, target_schema)
        unmodified = update_schema(unmodified, target_schema)
    return added, removed, modified, unmodified

def update_schema(item, schema):
    
    for k in item:
        try:
            if item[k].schema != schema:
                item[k].schema = schema
        except AttributeError:
            continue
    return item

def preprocess(od):
    od_list = list(od.keys())
    new_list = dict()
    for val in od_list:
        try:
            key = re.findall(r'\"\w+\"', val)[1]
        except Exception:
            key = re.findall(r'\"\w+\"', val)[0]
        new_list[val] = key
    # update the original od
    for k in new_list:
        od[new_list[k]] = od.pop(k)

    rev = {v: k for k, v in new_list.items()}
    return (od, set(od.keys()), rev)