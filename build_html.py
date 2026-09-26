import json
import os
import sys

# Add the parent directory to python path so we can import chip_viewer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chip_viewer import Chip, export_to_html

def convert_node(node):
    new_node = {}
    
    # Handle name
    if "Block_Name" in node:
        new_node["name"] = node["Block_Name"]
    elif "Name" in node:
        new_node["name"] = node["Name"]
    else:
        new_node["name"] = "Unnamed Block"
        
    # Handle specs (anything else that isn't sub_blocks)
    specs = {}
    for k, v in node.items():
        if k not in ["Block_Name", "Name", "Sub_Blocks", "Memory_and_Control", "Processing_Partitions"]:
            if isinstance(v, dict) or isinstance(v, list):
                specs[k] = json.dumps(v)
            else:
                specs[k] = str(v)
    if specs:
        new_node["specs"] = specs
        
    # Handle children
    children = []
    if "Sub_Blocks" in node:
        for child in node["Sub_Blocks"]:
            children.append(convert_node(child))
            
    if "Memory_and_Control" in node:
        mc_node = {"name": "Memory and Control", "children": []}
        for child in node["Memory_and_Control"]:
            mc_node["children"].append(convert_node(child))
        children.append(mc_node)
        
    if "Processing_Partitions" in node:
        pp_node = convert_node(node["Processing_Partitions"])
        if "name" not in pp_node or pp_node["name"] == "Unnamed Block":
            pp_node["name"] = "Processing Partitions"
        children.append(pp_node)
        
    if children:
        new_node["children"] = children
        
    return new_node

def main():
    input_file = "blackwell_block_diagram.json"
    
    with open(input_file, "r") as f:
        data = json.load(f)
        
    root = {
        "name": f"{data.get('Architecture', 'Architecture')} ({data.get('Project', 'marsg')})",
        "specs": {
            "Description": data.get("Description", ""),
            "Ecosystem_Integration": json.dumps(data.get("Ecosystem_Integration", {}))
        },
        "children": []
    }
    
    for block in data.get("Top_Level_Blocks", []):
        root["children"].append(convert_node(block))
        
    # save converted json
    converted_json = "converted_blackwell.json"
    with open(converted_json, "w") as f:
        json.dump(root, f, indent=4)
        
    # Export to HTML
    soc = Chip.from_json_file(converted_json)
    html_output = "blackwell_viewer.html"
    export_to_html(soc, html_output)
    print(f"Created HTML viewer at {os.path.abspath(html_output)}")

if __name__ == "__main__":
    main()
