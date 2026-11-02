import torch
from torch import nn

x_data = torch.tensor([[0.0], [1.0], [2.0], [3.0], [4.0]])
y_data = torch.tensor([[1.0], [3.0], [5.0], [7.0], [9.0]])

model = nn.Linear(1, 1)
loss_fn = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.05)

print("Starting guess: w =", round(model.weight.item(), 3),
      "b =", round(model.bias.item(), 3))

for step in range(300):
    pred = model(x_data)
    loss = loss_fn(pred, y_data)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 30 == 0:
        print(step, "loss:", round(loss.item(), 4))

print("Final: y=", round(model.weight.item(), 3), "x +",
      round(model.bias.item(), 3))