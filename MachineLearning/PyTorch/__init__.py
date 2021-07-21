'''PyTorch API'''

import torch
from pathlib import Path

from MachineLearning import HOME

MODELS = HOME / 'Models'
CHCKPNT = HOME / 'Checkpoints'
LOGS = HOME / 'Logs'

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
