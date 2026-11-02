import torch
from torch import nn

torch.manual_seed(0)
device = "cuda"

x = (torch.randn(64, 1, 32, 32) * 10).to(device)
target = (x[:, :, :, 2:] - x[:, :, :, :-2]) / 10

model = nn.Conv2d(1, 1, kernel_size=(1, 3), bias=False).to(device)
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

print("Starting kernel:",
      [round(v, 3) for v in model.weight.data.flatten().tolist()])

for step in range(500):
    pred = model(x)
    loss = loss_fn(pred, target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 50 == 0:
        print(step, "loss:", round(loss.item(), 6))

print("Learned kernel:",
      [round(v, 3) for v in model.weight.data.flatten().tolist()])