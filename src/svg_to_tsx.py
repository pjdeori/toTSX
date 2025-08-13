import os
import re

SVG_DIR = "./src/app/assets/icons/ui"         # where your SVGs are
OUTPUT_DIR = './src/app/components/icons/ui'  # where to save React components

os.makedirs(OUTPUT_DIR, exist_ok=True)

RESERVED_NAMES = {
    'react', 'class', 'default', 'return', 'function', 'export', 'var',
    'const', 'let', 'interface', 'enum', 'extends', 'implements', 'type',
    'await', 'async', 'static', 'super', 'new', 'this', 'switch',
    'case', 'break', 'continue', 'do', 'while', 'if', 'else', 'try',
    'catch', 'finally', 'throw', 'for', 'import', 'from'
}

def to_pascal_case(name):
    base = ''.join(word.capitalize() for word in re.split(r'[-_]', name))
    return base + 'Icon' if base.lower() in RESERVED_NAMES else base

def clean_svg(svg: str) -> str:
    # Extract <svg>...</svg>
    match = re.search(r'<svg[\s\S]*?</svg>', svg)
    if not match:
        return None
    svg = match.group(0)

    # Remove comments
    svg = re.sub(r'<!--.*?-->', '', svg, flags=re.DOTALL)

    # Remove fill, stroke, and style attributes
    svg = re.sub(r'\s+(fill|stroke|style)="[^"]*"', '', svg)

    # Add fill="currentColor" if not present in <svg> opening tag
    opening_tag = re.search(r'<svg[^>]*>', svg).group(0)
    if 'fill=' not in opening_tag:
        svg = svg.replace('<svg', '<svg fill="currentColor"', 1)

    return svg

def svg_to_react_component(svg_path, output_path):
    name = os.path.splitext(os.path.basename(svg_path))[0]
    component_name = to_pascal_case(name)

    with open(svg_path, 'r', encoding='utf-8') as f:
        raw_svg = f.read()

    svg = clean_svg(raw_svg)
    if not svg:
        print(f"❌ Skipped (no <svg>): {svg_path}")
        return

    svg_jsx = svg.strip()

    component_code = f"""// Generated from "{name}.svg" — auto-generated icon component

import React from 'react';

interface IconProps extends React.SVGProps<SVGSVGElement> {{
  className?: string;
  color?: string;
}}

const {component_name}: React.FC<IconProps> = ({{ className = "", color, ...props }}) => (
  React.cloneElement(
    {svg_jsx},
    {{
      className,
      ...(color ? {{ style: {{ color }} }} : {{}}),
      ...props
    }}
  )
);

export default {component_name};
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(component_code)

    print(f"✅ Converted: {name}.svg → {component_name}.tsx")

def process_folder(input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.endswith('.svg'):
                continue

            input_path = os.path.join(root, file)

            relative_path = os.path.relpath(root, input_dir)
            output_folder = os.path.join(output_dir, relative_path)
            os.makedirs(output_folder, exist_ok=True)

            output_file = os.path.splitext(file)[0] + '.tsx'
            output_path = os.path.join(output_folder, output_file)

            svg_to_react_component(input_path, output_path)

def generate_index(output_dir):
    index_path = os.path.join(output_dir, 'index.ts')
    exports = []

    for filename in os.listdir(output_dir):
        if filename.endswith('.tsx'):
            name = os.path.splitext(filename)[0]
            export_name = to_pascal_case(name)
            exports.append(f"export {{ default as {export_name} }} from './{name}';")

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(exports))

    print(f"📦 Generated {index_path} with {len(exports)} exports.")

if __name__ == "__main__":
    process_folder(SVG_DIR, OUTPUT_DIR)
    generate_index(OUTPUT_DIR)
