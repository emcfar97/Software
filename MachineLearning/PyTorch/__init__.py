'''PyTorch API'''

from pathlib import Path

from DeepLearning import HOME

MODELS = HOME / 'Pytorch' / 'Models'
CHCKPNT = HOME / 'Pytorch' / 'Checkpoints'
LOGS = HOME / 'Pytorch' / 'Logs'

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
