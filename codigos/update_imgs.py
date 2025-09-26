import os
import subprocess

# -------------------------------
# CONFIG
# -------------------------------
folder = "C:/Users/internet.info.ETECMOGIGUACU/PycharmProjects/NewTE Git/imagens"          # Folder containing your images
qrc_filename = "resources.qrc"
py_filename = "imgs_rc.py"  # Output Python module
prefix = "/"                # Resource prefix
image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")  # supported formats
# -------------------------------

# Step 1: Scan folder and generate .qrc content
qrc_content = ['<RCC>', f'    <qresource prefix="{prefix}">']

for filename in os.listdir(folder):
    if filename.lower().endswith(image_extensions):
        qrc_content.append(f'        <file>{folder}/{filename}</file>')

qrc_content.append('    </qresource>')
qrc_content.append('</RCC>')

# Write .qrc file
with open(qrc_filename, "w", encoding="utf-8") as f:
    f.write("\n".join(qrc_content))

print(f"[✓] Generated {qrc_filename} with {len(qrc_content)-3} files.")

# Step 2: Compile .qrc to Python module using pyrcc5
try:
    subprocess.run(["pyrcc5", qrc_filename, "-o", py_filename], check=True)
    print(f"[✓] Compiled {qrc_filename} → {py_filename}")
except FileNotFoundError:
    print("[✗] pyrcc5 not found. Make sure PyQt5 is installed and pyrcc5 is in PATH.")
except subprocess.CalledProcessError as e:
    print("[✗] Failed to compile .qrc:", e)
