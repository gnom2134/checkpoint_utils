## Autosave tool

### Description

Use ```SavableParams``` class to autosave all params that you need.

It is very convenient in case of unstable machine or working with services such as Google Colab or Kaggle Notebooks.

Simple interface:


```python
class SavableParams:
    def __init__(
        self,
        save_to: Path,
        autosave_period: int = 900,
        enable_autosaving: bool = True,
        force_restart: bool = False,
        **kwargs,
    ):
    """
    save_to: Path - path to the checkpoint
    autosave_period: int - how frequent you want autosave to trigger (in seconds)
    enable_autosaving: bool - turn on/off autosaving option
    force_restart: bool - to start from scratch or to try and load last checkpoint
    **kwargs - all your parameters should be placed here
    """
```

### Examples 

Code from [Simple neural network](examples/model_train.py)

```python
params = SavableParams(
    Path("./data/MNIST_example.pkl"),
    autosave_period=5,
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
while params.epoch < 10:
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

    print(f"Epoch [{params.epoch + 1}/{10}], Loss: {loss.item():.4f}")
    # update epoch num 
    params.epoch += 1

# stop autosaving - we won't need it anymore
params.interrupt()
# last save manually 
params.save()
```
Then we will interrupt our model during training and then rerun the script without any modifications to it.
```
# First run
Epoch [1/10], Loss: 0.1430
Epoch [2/10], Loss: 0.1828
Epoch [3/10], Loss: 0.0090

# Second run
Epoch [2/10], Loss: 0.0230
Epoch [3/10], Loss: 0.0054
Epoch [4/10], Loss: 0.0014
Epoch [5/10], Loss: 0.0021
Epoch [6/10], Loss: 0.2585
Epoch [7/10], Loss: 0.0299
Epoch [8/10], Loss: 0.0003

# Third run
Epoch [9/10], Loss: 0.0752
Epoch [10/10], Loss: 0.0030
Accuracy of the network on the 10000 test images: 98.02 %
```