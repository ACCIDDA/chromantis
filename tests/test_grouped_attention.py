"""Geographic message boundaries and missing-key handling are scientific constraints."""
import torch

from chromantis.model.network import SpatialBlock, grouped_attention


def test_group_boundary_blocks_values_and_gradients():
    torch.manual_seed(42)
    block = SpatialBlock(8)
    x = torch.randn(2, 4, 8, requires_grad=True)
    locations = ['a', 'b', 'c', 'd']
    groups = dict(a='TX', b='TX', c='NC', d='NC')
    observed = torch.ones(2, 4, dtype=torch.bool)
    out = grouped_attention(block, x, observed, locations, groups)
    changed = x.detach().clone()
    changed[:, 2:] = torch.randn_like(changed[:, 2:]) * 100
    other = grouped_attention(block, changed, observed, locations, groups)
    torch.testing.assert_close(out[:, :2], other[:, :2], rtol=0, atol=0)
    out[:, :2].square().sum().backward()
    assert x.grad[:, 2:].eq(0).all()
    assert x.grad[:, :2].abs().sum() > 0


def test_unobserved_keys_and_empty_group_do_not_send_messages():
    torch.manual_seed(43)
    block = SpatialBlock(8)
    x = torch.randn(1, 4, 8)
    locations = ['a', 'b', 'c', 'd']
    groups = dict(a='TX', b='TX', c='NC', d='NC')
    observed = torch.tensor([[True, False, False, False]])
    out = grouped_attention(block, x, observed, locations, groups)
    changed = x.clone()
    changed[:, 1] = torch.randn_like(changed[:, 1]) * 100
    other = grouped_attention(block, changed, observed, locations, groups)
    torch.testing.assert_close(out[:, 0], other[:, 0], rtol=0, atol=0)
    torch.testing.assert_close(out[:, 2:], x[:, 2:], rtol=0, atol=0)
    assert torch.isfinite(out).all()


def test_single_group_equals_unrestricted_attention():
    torch.manual_seed(44)
    block = SpatialBlock(8)
    x = torch.randn(2, 3, 8)
    observed = torch.tensor([[True, False, True], [False, False, False]])
    groups = dict(a='region', b='region', c='region')
    torch.testing.assert_close(
        grouped_attention(block, x, observed, ['a', 'b', 'c'], groups),
        block(x, observed), rtol=0, atol=0)
