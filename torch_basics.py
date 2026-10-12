import torch

x = torch.tensor(0.0, requires_grad=True)
learning_rate = 0.1

for step in range(20):
    y = (x - 5)**2
    y.backward()

    with torch.no_grad():
        x -= learning_rate * x.grad

    x.grad.zero_()
    print(step, round(x.item(), 4), round(y.item(), 4))