if __name__ == '__main__': from __init__ import *
else: from . import *
    
import torch

MODELS = HOME / 'Models'
CHCKPNT = HOME / 'Checkpoints'
LOGS = HOME / 'Logs'