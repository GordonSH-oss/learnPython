from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

FUNDAMENTALS = Path(__file__).parents[1]
sys.path.insert(0, str(FUNDAMENTALS))

from from_scratch import (  # noqa: E402
    CrossEntropyLoss,
    Linear,
    MLP,
    Momentum,
    ReLU,
    SGD,
    gradient_check,
    make_spiral,
    softmax,
    train_classifier,
)


def test_layers_and_loss_have_expected_shapes_and_values() -> None:
    inputs = np.array([[-1.0, 2.0], [3.0, -4.0]])
    linear = Linear(2, 3, seed=4)
    logits = linear.forward(inputs)
    activated = ReLU().forward(logits)
    probabilities = softmax(logits)
    loss = CrossEntropyLoss().forward(logits, np.array([0, 2]))

    assert logits.shape == activated.shape == probabilities.shape == (2, 3)
    assert np.all(activated >= 0)
    assert np.allclose(probabilities.sum(axis=1), 1.0)
    assert np.isfinite(loss) and loss > 0


def test_linear_and_cross_entropy_gradients_match_finite_differences() -> None:
    inputs = np.array([[0.2, -0.4], [1.1, 0.3], [-0.7, 0.8]])
    targets = np.array([0, 1, 0])
    layer = Linear(2, 2, seed=2)
    loss_function = CrossEntropyLoss()

    def loss_value() -> float:
        return loss_function.forward(layer.forward(inputs), targets)

    loss_value()
    layer.backward(loss_function.backward())
    error = gradient_check(loss_value, layer.weight, layer.grad_weight.copy())
    assert error < 1e-6


def test_optimizers_update_and_clear_gradients() -> None:
    layer = Linear(2, 2, seed=1)
    layer.grad_weight.fill(1.0)
    layer.grad_bias.fill(1.0)
    original = layer.weight.copy()
    optimizer = SGD(layer.parameters(), learning_rate=0.05)
    optimizer.step()
    assert not np.array_equal(layer.weight, original)
    optimizer.zero_grad()
    assert all(np.count_nonzero(gradient) == 0 for _, gradient in layer.parameters())

    layer.grad_weight.fill(1.0)
    momentum = Momentum(layer.parameters(), learning_rate=0.05, momentum=0.9)
    momentum.step()
    assert np.any(momentum.velocities[0] != 0)


def test_mlp_learns_small_spiral_problem() -> None:
    features, labels = make_spiral(samples_per_class=35, noise=0.12, seed=7)
    model = MLP(2, [32, 32], 3, seed=7)
    optimizer = Momentum(model.parameters(), learning_rate=0.08, momentum=0.9)
    history = train_classifier(model, features, labels, optimizer, epochs=180, batch_size=32, seed=7)

    assert history["loss"][-1] < history["loss"][0] * 0.55
    assert history["accuracy"][-1] >= 0.82
