# -*- coding: utf-8 -*-
from server import models


class TestShopIndex(object):
    def test_loads_data_on_init(self):
        shopindex = models.ShopIndex(filepath='tests/data/shops.csv')
        assert len(shopindex.geoindex.data.keys()) > 0

    def test_shops_within_radius(self):
        shopindex = models.ShopIndex(filepath='tests/data/shops.csv')

        shops = shopindex.shops_within_radius(59.33265972650577, 18.06061237898499, 3)

        assert len(shops) == 5

        last_distance = 0
        for shop in shops:
            assert shop.distance >= last_distance
            last_distance = shop.distance


class TestProductIndex(object):
    def test_loads_data_on_init(self):
        productindex = models.ProductIndex(filepath='tests/data/products.csv')
        assert len(productindex.keys()) > 0

    def test_products_in_shops(object):
        productindex = models.ProductIndex(filepath='tests/data/products.csv')
        shop_ids = ['32e563c14ef74098b10dc2207996544c', '059462d9341641a291ed3e5edb05c194']

        products = productindex.products_in_shops(shop_ids)

        last_popularity = 1
        for product in products:
            # Make sure it sored correctly.
            assert product.popularity <= last_popularity
            # Make sure it only returned products from shops in shop_ids.
            assert product.shop_id in shop_ids
            last_popularity = product.popularity

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
