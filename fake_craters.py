import numpy as np
import torch
from torch import nn
import matplotlib.pyplot as plt

torch.manual_seed(0)
rng = np.random.default_rng(0)
device = "cuda"
SIZE = 64


def make_tile():
    """One fake terrain tile with 1-4 bowl-shaped craters, plus its answer key."""
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    gx, gy = rng.uniform(-0.5, 0.5, size=2)
    z = gx * xx + gy * yy + rng.normal(0, 0.2, (SIZE, SIZE))
    mask = np.zeros((SIZE, SIZE))
    for _ in range(rng.integers(1, 5)):
        cx, cy = rng.uniform(8, SIZE - 8, size=2)
        r = rng.uniform(3, 8)
        dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
        inside = dist < r
        z[inside] -= 0.4 * r * (1 - (dist[inside] / r)**2)
        mask[inside] = 1
    z = (z - z.mean()) / z.std()
    return z, mask


def make_dataset(n):
    """n tiles and answer keys as GPU tensors shaped (n, 1, SIZE, SIZE)."""
    tiles, masks = zip(*[make_tile() for _ in range(n)])
    x = torch.tensor(np.array(tiles), dtype=torch.float32).unsqueeze(1)
    y = torch.tensor(np.array(masks), dtype=torch.float32).unsqueeze(1)
    return x.to(device), y.to(device)


x_train, y_train = make_dataset(512)
x_test, y_test = make_dataset(64)

model = nn.Sequential(
    nn.Conv2d(1, 16, kernel_size=5, padding=2), nn.ReLU(),
    nn.Conv2d(16, 16, kernel_size=5, padding=2), nn.ReLU(),
    nn.Conv2d(16, 16, kernel_size=5, padding=2), nn.ReLU(),
    nn.Conv2d(16, 1, kernel_size=1),
).to(device)

loss_fn = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for step in range(2000):
    loss = loss_fn(model(x_train), y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 50 == 0:
        with torch.no_grad():
            test_loss = loss_fn(model(x_test), y_test)
        print(step, "train loss:", round(loss.item(), 4),
              "test loss:", round(test_loss.item(), 4))

with torch.no_grad():
    prob = torch.sigmoid(model(x_test))
pred = (prob > 0.5).float()

with torch.no_grad():
    final_test_loss = loss_fn(model(x_test), y_test)
print("Final test loss:", round(final_test_loss.item(), 4))

i = 0
fig, axes = plt.subplots(1, 3)
axes[0].imshow(x_test[i, 0].cpu().numpy(), cmap="gray")
axes[0].set_title("Terrain")
axes[1].imshow(y_test[i, 0].cpu().numpy(), cmap="gray")
axes[1].set_title("True craters")
axes[2].imshow(pred[i, 0].cpu().numpy(), cmap="gray")
axes[2].set_title("Predicted")
plt.show()