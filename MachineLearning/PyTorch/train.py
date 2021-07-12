'''File for training, saving, and loading models'''

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

class Model():

    def __init__(self): pass

    def train(self):

        size = len(dataloader.dataset)
        
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(DEVICE), y.to(DEVICE)

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
                
        epochs = 5

        for t in range(epochs):

            print(f"Epoch {t+1}\n-------------------------------")
            train(train_dataloader, model, loss_fn, optimizer)
            test(test_dataloader, model, loss_fn)

    def test(self):

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
        
        epochs = 5

        for t in range(epochs):

            print(f"Epoch {t+1}\n-------------------------------")
            train(train_dataloader, model, loss_fn, optimizer)
            test(test_dataloader, model, loss_fn)

    def predict(self):

        model.eval()
        x, y = test_data[0][0], test_data[0][1]
        with torch.no_grad():
            pred = model(x)
            predicted, actual = classes[pred[0].argmax(0)], classes[y]
            print(f'Predicted: "{predicted}", Actual: "{actual}"')

    def save(self): 
        
        torch.save(self.model.state_dict(), "model.pth")
        print("Saved PyTorch Model State to model.pth")

    def load(self):
        
        model = NeuralNetwork()
        model.load_state_dict(torch.load("model.pth"))

# Transformation
transform = transforms.Compose([
transforms.Resize((256, 256)),
transforms.ToTensor(),
transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

train_data_tensor = Custom_Dataset(train_data_dir, transform=transform)

def train(dataloader, model, loss_fn, optimizer):
        
def test(dataloader, model, loss_fn):


epochs = 5

for t in range(epochs):

    print(f"Epoch {t+1}\n-------------------------------")
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)

print("Done!")