"""
cointracker is a work-in-progress package that converts cryptocurrency transactions from an order book
into purchase and sale pools and exports this info for tax purposes.

It currently requires the order books to be input in a specific format and only supports the LIFO accounting
method.
"""

# import the subpackages
from cointracker import run, pricing, util
"""
__all__ = [
        'run',
        'pricing',
        'util',
        ]
"""
# from .getAssetPrice import getAssetPrice
# why does this kill the ability to find CoinTracker.A when called?

print(f'Invoking __init__.py for {__name__}')
# A = ['quux', 'corge', 'grault']
