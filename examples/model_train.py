import torch
import torchvision
from src.checkpoint import SavableParams
from pathlib import Path


class LinearModel(torch.nn.Module):
    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.ll1 = torch.nn.Linear(in_dim, 32)
        self.relu = torch.nn.ReLU()
        self.ll2 = torch.nn.Linear(32, out_dim)

    def forward(self, x: torch.Tensor):
        return self.ll2(self.relu(self.ll1(x)))


if __name__ == "__main__":
    train_data = torchvision.datasets.MNIST(
        root="./data", train=True, download=True, transform=torchvision.transforms.ToTensor()
    )
    test_data = torchvision.datasets.MNIST(
        root="./data", train=False, download=True, transform=torchvision.transforms.ToTensor()
    )

    train_loader = torch.utils.data.DataLoader(train_data, batch_size=4, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=4, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LinearModel(28 * 28, 10)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    criterion = torch.nn.CrossEntropyLoss()

    params = SavableParams(
        Path("./data/MNIST_example.pkl"),
        every_n_seconds=10,
        enable_autosaving=True,
        force_restart=False,
        # Custom parameters here
        epoch=0,
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
    )

    n_total_steps = len(params.train_loader)
    # access epoch num
    while params.epoch < 3:
        for i, (images, labels) in enumerate(params.train_loader):
            images = images.reshape(-1, 28 * 28).to(device)
            labels = labels.to(device)
            # access model
            outputs = params.model(images)
            loss = criterion(outputs, labels)
            # access optimizer
            params.optimizer.zero_grad()
            loss.backward()
            # access optimizer again
            params.optimizer.step()

        print(f"Epoch [{params.epoch + 1}/{3}], Loss: {loss.item():.4f}")
        # update epoch num
        params.epoch += 1

    # stop autosaving - we won't need it anymore
    params.interrupt()
    # last save manually
    params.save()

    with torch.no_grad():
        n_correct = 0
        n_samples = 0
        for images, labels in test_loader:
            images = images.reshape(-1, 28 * 28).to(device)
            labels = labels.to(device)
            outputs = params.model(images)
            _, predicted = torch.max(outputs.data, 1)
            n_samples += labels.size(0)
            n_correct += (predicted == labels).sum().item()
        acc = 100.0 * n_correct / n_samples
        print(f"Accuracy of the network on the 10000 test images: {acc} %")
