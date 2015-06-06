# -*- coding: utf-8 -*-
from server import models


class TestShopIndex(object):
    def test_loads_data_on_init(self):
        shopindex = models.ShopIndex(shops='tests/data/shops.csv')
        assert len(shopindex.keys()) > 0

    def test_loads_tags(self):
        shopindex = models.ShopIndex(shops='tests/data/shops.csv', taggings='tests/data/taggings.csv')

        shop = shopindex['4aa53e646bf84faca9a76c020b0682de']
        assert len(shop['tags']) == 2

    def test_shops_within_radius(self):
        shopindex = models.ShopIndex(shops='tests/data/shops.csv')

        shops = shopindex.shops_within_radius(59.33265972650577, 18.06061237898499, 3)

        assert len(list(shops)) == 5

    def test_shops_within_radius_tags(self):
        shopindex = models.ShopIndex(shops='tests/data/shops.csv', taggings='tests/data/taggings.csv')

        tags = ['4202dd8da64d4ebea7577f0f2b2e991b', '10e0e321984842cb877941ff66f7f349']

        shops = shopindex.shops_within_radius(59.33265972650577, 18.06061237898499, 3, tags)

        assert len(list(shops)) == 1


class TestTagIndex(object):
    def test_loads_data_on_init(self):
        tagindex = models.TagIndex(tags='tests/data/tags.csv')
        assert len(tagindex.keys()) > 0


class TestProductIndex(object):
    def test_loads_data_on_init(self):
        productindex = models.ProductIndex(filepath='tests/data/products.csv')
        assert len(productindex.keys()) > 0

    def test_products_in_shops(object):
        productindex = models.ProductIndex(filepath='tests/data/products.csv')
        shop_ids = ['32e563c14ef74098b10dc2207996544c', '059462d9341641a291ed3e5edb05c194']

        products = productindex.products_in_shops(shop_ids)

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
