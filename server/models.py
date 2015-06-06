# -*- coding: utf-8 -*-
import csv
import geoindex
import itertools


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
            shop['lat'] = float(shop['lat'])
            shop['lng'] = float(shop['lng'])
            shop['tags'] = tags.get(shop['id'], [])

            self[shop['id']] = shop

            self.geoindex.add_point(
                geoindex.GeoPoint(
                    shop['lat'],
                    shop['lng'],
                    ref=shop
                )
            )

    def shops_within_radius(self, lat, lng, radius, tags=None):
        center_point = geoindex.GeoPoint(lat, lng)
        points = self.geoindex.get_nearest_points(center_point, radius, 'km')

        def tags_filter(shops):
            for shop in shops:
                for tag in tags:
                    if tag in shop['tags']:
                        yield shop
                        break

        def get_shops():
            for point, distance in points:
                point.ref['distance'] = distance
                yield point.ref

        if tags:
            return get_shops()
        else:
            return tags_filter(get_shops())


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
        for product in load_data(filepath):
            if product['shop_id'] not in self:
                self[product['shop_id']] = []

            product['popularity'] = float(product['popularity'])
            product['quantity'] = int(product['quantity'])
            self[product['shop_id']].append(product)

    def products_in_shops(self, shop_ids):
        """
        Returns a list of products in `shop_ids`, sorted by popularity.
        """
        for product in itertools.chain(*(self.get(shop_id, []) for shop_id in shop_ids)):
            yield product


def load_data(filepath):
    """
    Iterator.
    Loads data from a csv file and yields dicts for each row.
    """
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row
