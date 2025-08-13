import os
import re

SVG_DIR = "./src/app/assets/icons/ui"         # where your SVGs are
OUTPUT_DIR = './src/app/assets/components/icons/ui'  # where to save React components
INDEX_FILE = os.path.join(OUTPUT_DIR, 'index.ts')     # index file to generate

os.makedirs(OUTPUT_DIR, exist_ok=True)

def kebab_or_snake_to_pascal(name):
    return ''.join(word.capitalize() for word in re.split(r'[-_]', name))

def svg_to_react_component(svg_path, output_path, export_list):
    name = os.path.splitext(os.path.basename(svg_path))[0]
    component_name = kebab_or_snake_to_pascal(name)

    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    # Extract only the <svg>...</svg> block
    match = re.search(r'<svg[\s\S]*?</svg>', svg)
    if not match:
        print(f"❌ No <svg> tag found in {svg_path}")
        return
    svg = match.group(0)

    # Clean attributes: remove hardcoded colors/styles
    svg = re.sub(r'\s(fill|stroke|style)="[^"]*"', '', svg)

    # Add `fill="currentColor"` if not present
    if 'fill=' not in svg.split('>')[0]:
        svg = svg.replace('<svg', '<svg fill="currentColor"', 1)

    # Inject `className` and props into <svg>
    svg = svg.replace('<svg', '<svg className={className} {...props}', 1)

    # Wrap in a React component
    component_code = f"""import React from 'react';

const {component_name} = ({{ className = "", ...props }}) => (
  {svg}
);

export default {component_name};
"""

    # Write the .tsx file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(component_code)

    export_list.append(f"export {{ default as {component_name} }} from './{name}';")
    print(f"✅ Converted: {name}.svg → {component_name}.tsx")

def process_folder(svg_dir, output_dir):
    export_lines = []

    for root, _, files in os.walk(svg_dir):
        for file in files:
            if file.endswith('.svg'):
                input_path = os.path.join(root, file)

                # Maintain folder structure if needed
                relative_path = os.path.relpath(root, svg_dir)
                output_folder = os.path.join(output_dir, relative_path)
                os.makedirs(output_folder, exist_ok=True)

                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_folder, f"{base_name}.tsx")

                svg_to_react_component(input_path, output_path, export_lines)

    # Write index.ts with all exports
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(export_lines)))
    print(f"\n🧾 index.ts created with {len(export_lines)} exports at: {INDEX_FILE}")

if __name__ == "__main__":
    process_folder(SVG_DIR, OUTPUT_DIR)
