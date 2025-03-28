import argparse
import json
import hashlib
import sys

def sha256_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def load_tree(filename="merkle.tree"):
    with open(filename, "r") as f:
        return json.load(f)

def get_inclusion_proof(tree, target_data):
    # Look for the target string in the leaves.
    leaves = tree.get("leaves", [])
    target_index = None
    for i, leaf in enumerate(leaves):
        if leaf.get("data") == target_data:
            target_index = i
            break
    if target_index is None:
        return None  # Target not found.
    
    proof = []
    levels = tree.get("levels", [])
    index = target_index
    # For each level, add the sibling hash (if exists) to the proof.
    for level in levels:
        if index % 2 == 0:
            sibling_index = index + 1
            if sibling_index < len(level):
                proof.append(level[sibling_index])
        else:
            sibling_index = index - 1
            proof.append(level[sibling_index])
        index //= 2  # Move to parent's index.
    return proof

def main():
    parser = argparse.ArgumentParser(description="Check inclusion in Merkle Tree")
    parser.add_argument("target", help="The string to check for inclusion in the Merkle tree")
    args = parser.parse_args()
    
    try:
        tree = load_tree()
    except Exception as e:
        print(f"Error loading merkle.tree: {e}")
        sys.exit(1)
    
    proof = get_inclusion_proof(tree, args.target)
    if proof is None:
        print("no")
    else:
        print("yes", proof)

if __name__ == "__main__":
    main()
