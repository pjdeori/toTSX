import os
import re

SVG_DIR = "../assets/svg_icons"
OUTPUT_DIR = '../assets/tsx_components'

def svg_to_react_component(svg_path, output_path):
    name = os.path.splitext(os.path.basename(svg_path))[0]
    # Convert kebab-case or snake_case to PascalCase for React component name
    component_name = ''.join(word.capitalize() for word in re.split('[-_]', name))

    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    # Extract only the <svg>...</svg> part, strip XML declarations or comments
    match = re.search(r'<svg[\s\S]*?</svg>', svg)
    if not match:
        print(f"❌ No <svg> tag found in {svg_path}")
        return
    svg = match.group(0)

    # Remove fill, stroke, style attributes
    svg = re.sub(r'\s(fill|stroke|style)="[^"]*"', '', svg)

    # Add fill="currentColor" if missing in the opening <svg> tag
    svg_opening_tag = re.search(r'<svg[^>]*>', svg).group(0)
    if 'fill=' not in svg_opening_tag:
        svg = svg.replace('<svg', '<svg fill="currentColor"', 1)

    # Build React component string
    component = f"""import React from 'react';

const {component_name} = ({{ className = "", ...props }}) => (
  {svg.replace('<svg', '<svg className={className} {...props}')}
);

export default {component_name};
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(component)

    print(f"✅ Converted: {name}.svg → {component_name}.tsx")

if __name__ == "__main__":

    # creates directory if needed.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for root, dirs, files in os.walk(SVG_DIR):
        for file in files:
            if file.endswith('.svg'):
                # get input path
                input_path = os.path.join(root, file)

                # get output folder structure (mirrors source structure)
                relative_path = os.path.relpath(root, SVG_DIR) # get sub dir
                output_folder = os.path.join(OUTPUT_DIR, relative_path) # get output+sub dir

                # creates directory if needed.
                os.makedirs(output_folder, exist_ok=True)

                # splits filename to a tuple(name, extension)
                filename = os.path.splitext(file)[0]

                # adds tsx as extension
                output_filename = filename + ".tsx"

                # get output path
                output_path = os.path.join(output_folder, output_filename)

                # process the file
                svg_to_react_component(input_path, output_path)