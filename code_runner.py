import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import traceback
import sys
import io
import os

# Redirect output to capture it
output_buffer = io.StringIO()
sys.stdout = output_buffer
sys.stderr = output_buffer

# Clear old plot
if os.path.exists("output.png"):
    os.remove("output.png")

# Safe override for plt.show()
plt.show = lambda: None

# Execute generated script
try:
    with open("generated_script.py", "r") as f:
        code = f.read()
    exec(code, {"__name__": "__main__"})

    if plt.get_fignums():
        plt.savefig("output.png")

except Exception:
    traceback.print_exc()

# Print captured output
print(output_buffer.getvalue())
