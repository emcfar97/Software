import argparse

parser = argparse.ArgumentParser(
    prog='Machine Learning', 
    description='Command line interface for common ML operations and projects'
    )
parser.add_argument(
    '-n', '--num', type=int,
    help='Number of streams', default=2
    )
args = parser.parse_args()

from .dataset import Custom_Dataset
from .. import BATCH, EPOCH

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor

class NeuralNetwork(nn.Module):

    def __init__(self):

        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
            nn.ReLU()
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

# Get cpu or gpu device for training.
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using {} device".format(device))

# Dataset

# Download training data from open datasets.
data = Custom_Dataset(
    main_dir="Medium", transform=ToTensor(),
    )
train_loader = DataLoader(
    data, batch_size=BATCH, shuffle=False, 
    num_workers=4, drop_last=True
    )

# Design
# Define model
model = NeuralNetwork().to(device)
print(model)

# Train
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

for t in range(EPOCH):

    print(f"Epoch {t+1}\n-------------------------------")
    train(train_loader, model, loss_fn, optimizer)
    # test(test_dataloader, model, loss_fn)

print("Done!")

torch.save(model.state_dict(), "model.pth")
print("Saved PyTorch Model State to model.pth")

model = NeuralNetwork()
model.load_state_dict(torch.load("model.pth"))

model.eval()
x, y = data[0][0], data[0][1]

with torch.no_grad():

    pred = model(x)
    predicted, actual = data.class_names[pred[0].argmax(0)], data.class_names[y]
    print(f'Predicted: "{predicted}", Actual: "{actual}"')