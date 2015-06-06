# -*- coding: utf-8 -*-
"""
products.csv
shops.csv
taggings.csv
tags.csv
"""
import csv
import operator
import geoindex
import itertools


class Shop(object):
    def __init__(self, id, name, lat, lng, tags=None):
        self.id = id
        self.name = name
        self.lat = float(lat)
        self.lng = float(lng)
        self.distance = None
        self.tags = tags


class Product(object):
    def __init__(self, id, shop_id, title, popularity, quantity):
        self.id = id
        self.shop_id = shop_id
        self.title = title
        self.popularity = float(popularity)
        self.quantity = float(quantity)


class TagIndex(dict):
    def __init__(self, tags):
        for tag in load_data(tags):
            self[tag['id']] = tag['tag']


class ShopIndex(dict):
    """
    Index of shops.
    Wrapper around `geindex.GeoGridIndex` for spatial indexing of shops
    The data is loaded when this class is initialized.
    """
    def __init__(self, shops, taggings=None):
        """
        Loads data from `filepath`.
        """
        self.geoindex = geoindex.GeoGridIndex(precision=4)
        tags = {}

        if taggings:
            for tag in load_data(taggings):
                if not tag['shop_id'] in tags:
                    tags[tag['shop_id']] = []
                tags[tag['shop_id']].append(tag['tag_id'])

        for shop in load_data(shops):
            shop_object = Shop(
                tags=tags.get(shop['id'], None),
                **shop
            )
            self[shop['id']] = shop_object

            self.geoindex.add_point(
                geoindex.GeoPoint(
                    shop_object.lat,
                    shop_object.lng,
                    ref=shop_object
                )
            )

    def shops_within_radius(self, lat, lng, radius):
        def get_shops():
            center_point = geoindex.GeoPoint(lat, lng)
            points = self.geoindex.get_nearest_points(center_point, radius, 'km')

            for point, distance in points:
                point.ref.distance = distance
                yield point.ref

        return sort_by(get_shops(), 'distance')


class ProductIndex(dict):
    """
    The index of products, this is a subclass of `dict` with extra convenience methods.
    Each `key` is the id of a shop.
    The data is loaded when this class is initialized.
    """
    def __init__(self, filepath):
        """
        Loads data from `filepath`.
        """
        products = load_data(filepath)

        for product in products:
            product_obj = Product(**product)

            if product_obj.shop_id not in self:
                self[product_obj.shop_id] = []

            self[product_obj.shop_id].append(product_obj)

    def products_in_shops(self, shop_ids):
        """
        Returns a list of products in `shop_ids`, sorted by popularity.
        """
        def get_products():
            for product in itertools.chain(*(self[shop_id] for shop_id in shop_ids)):
                yield product

        return sort_by(get_products(), 'popularity', True)


def sort_by(items, by, reverse=False):
    """
    Sorts a list/iterator.
    `by` needs to be an attribute of each item.
    """
    return sorted(items, key=operator.attrgetter(by), reverse=reverse)


def load_data(filepath):
    """
    Iterator.
    Loads data from a csv file and yields dicts for each row.
    """
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row
