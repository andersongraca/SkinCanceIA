import json
import platform
import sys

import torch

result = {
    "python": sys.version,
    "platform": platform.platform(),
    "torch": torch.__version__,
    "cuda_available": bool(torch.cuda.is_available()),
    "cuda_version": torch.version.cuda,
    "device_count": torch.cuda.device_count(),
    "devices": [],
}
for index in range(torch.cuda.device_count()):
    result["devices"].append({
        "index": index,
        "name": torch.cuda.get_device_name(index),
        "memory_gb": round(torch.cuda.get_device_properties(index).total_memory / (1024**3), 2),
    })
print(json.dumps(result, indent=2, ensure_ascii=False))
