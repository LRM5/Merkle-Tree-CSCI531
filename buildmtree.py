import argparse
import json
import hashlib
import sys

def sha256_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def parse_input_list(input_str):
    # Remove surrounding square brackets if present and split by comma.
    input_str = input_str.strip()
    if input_str.startswith('[') and input_str.endswith(']'):
        input_str = input_str[1:-1]
    # Split by comma and remove extra whitespace.
    return [s.strip() for s in input_str.split(',') if s.strip()]

def build_merkle_tree(leaves_data):
    # Build level 0: the leaves (store both original data and hash).
    leaves = []
    for data in leaves_data:
        node = {"data": data, "hash": sha256_hash(data)}
        leaves.append(node)
    levels = []
    # Level 0 stores the hash values of the leaves.
    levels.append([node["hash"] for node in leaves])
    
    # Build the upper levels by pairing hashes.
    current_level = leaves
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]["hash"]
            if i + 1 < len(current_level):
                right = current_level[i+1]["hash"]
            else:
                # Duplicate the last hash if odd number of nodes.
                right = left
            parent_hash = sha256_hash(left + right)
            node = {"hash": parent_hash, "left": left, "right": right}
            next_level.append(node)
        levels.append([node["hash"] for node in next_level])
        current_level = next_level
    return leaves, levels

def main():
    parser = argparse.ArgumentParser(description="Build Merkle Tree")
    parser.add_argument("data", help="List of strings for merkle tree, e.g., \"[alice, bob, carlol, david]\"")
    args = parser.parse_args()
    
    leaves_data = parse_input_list(args.data)
    if not leaves_data:
        print("Error: No valid data provided.")
        sys.exit(1)
        
    leaves, levels = build_merkle_tree(leaves_data)
    tree = {
        "leaves": leaves,
        "levels": levels,
        "root": levels[-1][0] if levels and levels[-1] else None
    }
    
    with open("merkle.tree", "w") as f:
        json.dump(tree, f, indent=4)
    print("Merkle tree built successfully. Output saved to merkle.tree")

if __name__ == "__main__":
    main()
