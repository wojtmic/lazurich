from lazurich.core.utils import gen_id
from random import seed

def test_gen_id_no_collisions():
    seed(0)
    ids = [gen_id() for _ in range(1_000_000)]
    assert len(ids) == len(set(ids))
