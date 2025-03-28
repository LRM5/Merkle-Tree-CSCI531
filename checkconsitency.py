import argparse
import json
import hashlib
import sys

def sha256_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def parse_input_list(input_str):
    # Remove square brackets if present and split by comma.
    input_str = input_str.strip()
    if input_str.startswith('[') and input_str.endswith(']'):
        input_str = input_str[1:-1]
    return [s.strip() for s in input_str.split(',') if s.strip()]

def build_merkle_tree(leaves_data):
    # Build level 0: the leaves (store both original data and hash).
    leaves = []
    for data in leaves_data:
        node = {"data": data, "hash": sha256_hash(data)}
        leaves.append(node)
    levels = []
    levels.append([node["hash"] for node in leaves])
    
    current_level = leaves
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]["hash"]
            if i + 1 < len(current_level):
                right = current_level[i+1]["hash"]
            else:
                right = left
            parent_hash = sha256_hash(left + right)
            node = {"hash": parent_hash, "left": left, "right": right}
            next_level.append(node)
        levels.append([node["hash"] for node in next_level])
        current_level = next_level
    return leaves, levels

def get_consistency_proof(old_leaves, new_levels):
    # A simplified consistency proof computation.
    # For each level in the new tree, derive a sibling hash based on the index of the last old leaf.
    n = len(old_leaves)
    proof = []
    index = n - 1
    for level in new_levels[:-1]:
        if index % 2 == 0:
            sibling_index = index + 1
            if sibling_index < len(level):
                proof.append(level[sibling_index])
        else:
            sibling_index = index - 1
            proof.append(level[sibling_index])
        index //= 2
    return proof

def main():
    parser = argparse.ArgumentParser(description="Check consistency between two Merkle Trees")
    parser.add_argument("old_data", help="Old list of strings, e.g., \"[alice, bob, carlol, david]\"")
    parser.add_argument("new_data", help="New list of strings, e.g., \"[alice, bob, carlol, david, eve, fred]\"")
    args = parser.parse_args()
    
    old_list = parse_input_list(args.old_data)
    new_list = parse_input_list(args.new_data)
    
    # Verify that old_list is a prefix of new_list.
    if new_list[:len(old_list)] != old_list:
        # Trees are inconsistent.
        old_leaves, old_levels = build_merkle_tree(old_list)
        new_leaves, new_levels = build_merkle_tree(new_list)
        trees = {"old_tree": old_levels, "new_tree": new_levels}
        with open("merkle.trees", "w") as f:
            json.dump(trees, f, indent=4)
        print("no")
        sys.exit(0)
    
    # Build trees for consistency proof.
    old_leaves, old_levels = build_merkle_tree(old_list)
    new_leaves, new_levels = build_merkle_tree(new_list)
    
    # Generate a simplified consistency proof.
    proof = get_consistency_proof(old_leaves, new_levels)
    
    # Save both trees to merkle.trees for user inspection.
    trees = {"old_tree": old_levels, "new_tree": new_levels}
    with open("merkle.trees", "w") as f:
        json.dump(trees, f, indent=4)
    
    print("yes", proof)

if __name__ == "__main__":
    main()
