# -*- coding: utf-8 -*-
from server import models


class TestShopIndex(object):
    def test_loads_data_on_init(self):
        shopindex = models.ShopIndex(shops='tests/data/shops.csv')
        assert len(shopindex.keys()) > 0

    def test_loads_tags(self):
        shopindex = models.ShopIndex(
            shops='tests/data/shops.csv',
            tags='tests/data/tags.csv',
            taggings='tests/data/taggings.csv'
        )

        shop = shopindex['4aa533646bf84faca9a76c020b0682de']
        assert len(shop['tags']) == 1

    def test_shops_within_radius(self):
        shopindex = models.ShopIndex(shops='tests/data/shops.csv')

        shops = shopindex.shops_within_radius(59.33265972650577, 18.06061237898499, 3)

        assert len(list(shops)) == 5

    def test_shops_within_radius_tags(self):
        shopindex = models.ShopIndex(
            shops='tests/data/shops.csv',
            tags='tests/data/tags.csv',
            taggings='tests/data/taggings.csv'
        )

        tags = ['trousers', 'somethingelse']

        shops = shopindex.shops_within_radius(59.33265972650577, 18.06061237898499, 3, tags)

        assert len(list(shops)) == 1


class TestProductIndex(object):
    def test_loads_data_on_init(self):
        productindex = models.ProductIndex(filepath='tests/data/products.csv')
        assert len(productindex.keys()) > 0

    def test_products_in_shops(object):
        productindex = models.ProductIndex(filepath='tests/data/products.csv')
        shops = [{'id': '32e563c14ef74098b10dc2207996544c'}, {'id': '059462d9341641a291ed3e5edb05c194'}]

        products = productindex.products_in_shops(shops)

        assert len(list(products)) == 2

    def __test_performance(self):
        import timeit

        # products_large contains all products.
        productindex = models.ProductIndex(filepath='tests/data/products_large.csv')

        # test data contains only 9 shops.
        shop_ids = [item['id'] for item in models.load_data('tests/data/shops.csv')]

        def do_it():
            products = productindex.products_in_shops(shop_ids)
            for product in products:
                product.shop_id

        t = timeit.timeit(do_it, number=500)
        assert t < 0.02
