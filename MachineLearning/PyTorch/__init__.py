'''PyTorch API'''

if __name__ in ('__main__', '__init__'): from __init__ import *
else: from . import *

import torch
from pathlib import Path

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
HOME = Path(__file__).parent
MODELS = HOME / 'Models'
CHCKPNT = HOME / 'Checkpoints'
LOGS = HOME / 'Logs'
BATCH = 64