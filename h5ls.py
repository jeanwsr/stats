#!/usr/bin/env python
import h5py
import sys
import re

def clean_key_name(key):
    """Remove __from_list__ suffix from key names"""
    return re.sub(r'__from_list__$', '', key)

def collect_hdf5_structure(name, obj):
    """Recursively collect HDF5 structure info"""
    if isinstance(obj, h5py.Dataset):
        is_in_list_group = '__from_list__' in name
        is_list_group = name.endswith('__from_list__')
        
        if is_list_group and len(obj.shape) >= 1:
            return ('list', clean_key_name(name), obj.shape, obj.dtype)
        elif is_list_group:
            return ('list', clean_key_name(name), 'scalars', obj.dtype)
        elif is_in_list_group:
            parent_clean = clean_key_name(name.rsplit('/', 1)[0])
            return ('list_member', parent_clean, obj.shape, obj.dtype)
        else:
            return ('dataset', clean_key_name(name), obj.shape, obj.dtype)
    elif isinstance(obj, h5py.Group):
        if name != '/':
            return ('group', clean_key_name(name))
    return None

def print_hdf5_structure(items):
    """Print compact HDF5 structure with grouped lists"""
    list_groups = {}
    regular_items = []
    
    for item in items:
        if item is None:
            continue
        if item[0] == 'list':
            typ, name, shape, dtype = item
            key = (name, shape, dtype)
            if key not in list_groups:
                list_groups[key] = 0
            list_groups[key] += 1
        elif item[0] == 'list_member':
            typ, name, shape, dtype = item
            key = (name, shape, dtype)
            if key not in list_groups:
                list_groups[key] = 0
            list_groups[key] += 1
        else:
            regular_items.append(item)
    
    for item in regular_items:
        indent = ""
        if item[0] == 'group':
            print(f"{indent}{item[1]}/")
        else:
            print(f"{indent}{item[1]}: {item[2]} {item[3]}")
    
    for (name, shape, dtype), count in list_groups.items():
        shape_str = shape if shape != 'scalars' else 'scalars'
        print(f"{name}: list[{count}] of {shape_str} {dtype}")

def list_hdf5_contents(filename):
    """List HDF5 contents in compact format"""
    try:
        with h5py.File(filename, 'r') as f:
            items = []
            f.visititems(lambda name, obj: items.append(collect_hdf5_structure(name, obj)))
            
            print(f"\n{filename}")
            print("-" * 50)
            print_hdf5_structure(items)
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <hdf5_filename>")
        sys.exit(1)
    
    list_hdf5_contents(sys.argv[1])
