import torch

x_data = torch.tensor([0.0, 1.0, 2.0, 3.0, 4.0])
y_data = torch.tensor([1.0, 3.0, 5.0, 7.0, 9.0])

w = torch.tensor(0.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
learning_rate = 0.05

for step in range(300):
    pred = w * x_data + b
    loss = ((pred - y_data)**2).mean()
    loss.backward()

    with torch.no_grad():
        w -= learning_rate * w.grad
        b -= learning_rate * b.grad

    w.grad.zero_()
    b.grad.zero_()

    if step % 30 == 0:
        print(step, "loss:", round(loss.item(), 4),
              "w:", round(w.item(), 3), "b:", round(b.item(), 3))

print("Final: y =", round(w.item(), 3), "x +", round(b.item(), 3))