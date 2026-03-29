import h5py
import sys
import re

def clean_key_name(key):
    """Remove __from_list__ suffix from key names"""
    return re.sub(r'__from_list__$', '', key)

def print_hdf5_structure(name, obj, level=0):
    """Recursively print compact HDF5 structure"""
    indent = "  " * level
    clean_name = clean_key_name(name)
    
    if isinstance(obj, h5py.Dataset):
        is_list = '__from_list__' in name
        if is_list and len(obj.shape) >= 2:
            # List of arrays
            member_shape = obj.shape[1:]
            print(f"{indent}{clean_name}: list[{obj.shape[0]}] of {member_shape} {obj.dtype}")
        elif is_list:
            # List of scalars
            print(f"{indent}{clean_name}: list[{obj.shape[0]}] of scalars {obj.dtype}")
        else:
            # Regular dataset
            print(f"{indent}{clean_name}: {obj.shape} {obj.dtype}")
    elif isinstance(obj, h5py.Group):
        if name != '/':
            print(f"{indent}{clean_name}/")
            level += 1

def list_hdf5_contents(filename):
    """List HDF5 contents in compact format"""
    try:
        with h5py.File(filename, 'r') as f:
            print(f"\n{filename}")
            print("-" * 50)
            f.visititems(lambda name, obj: print_hdf5_structure(name, obj))
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <hdf5_filename>")
        sys.exit(1)
    
    list_hdf5_contents(sys.argv[1])
