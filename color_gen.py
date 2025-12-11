import plotly.express as px
import colorsys
import re

def rgb_str_to_hsv(rgb_str):
    # Parse "rgb(r, g, b)"
    match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
    if match:
        r, g, b = map(int, match.groups())
        return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    return (0, 0, 0)

def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))

original_colors = px.colors.qualitative.Bold
new_colors = []

print(f"Original: {original_colors}")

for c in original_colors:
    if c.startswith('rgb'):
        h, s, v = rgb_str_to_hsv(c)
    else:
        # Fallback if it is hex (though unlikely strictly for Bold)
        continue
        
    # 1. Minimize saturation by 20%
    s = max(0, s * 0.8)
    
    # 2. Check for Pink/Magenta and change it
    # Hue usually runs 0-1. Pink/Magenta is around 0.8-0.95
    # Red is around 0 or 1.
    # 0.9 is Magenta/Pink
    if 0.8 < h < 0.98: 
        print(f"Replacing Pink hue: {h}")
        h = 0.5 # Change to Cyan/Teal
        
    new_colors.append(hsv_to_hex(h, s, v))

with open('colors.txt', 'w') as f:
    f.write(str(new_colors))

