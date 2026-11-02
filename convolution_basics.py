import torch
import torch.nn.functional as F

terrain = torch.tensor([[100.0, 102.0, 105.0],
                        [ 98.0, 100.0, 110.0],
                        [ 95.0,  97.0, 120.0]])

x = terrain.reshape(1, 1, 3, 3)

kernel = torch.tensor([[-1.0, 0.0, 1.0]]) / 10
k = kernel.reshape(1, 1, 1, 3)

out = F.conv2d(x, k)
print(out)
print(out.shape)