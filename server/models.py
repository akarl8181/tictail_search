# -*- coding: utf-8 -*-
import csv
import geoindex


class ShopIndex(dict):
    """
    Index of shops.
    Wrapper around `geindex.GeoGridIndex` for spatial indexing of shops
    The data is loaded when this class is initialized.
    """
    def __init__(self, shops, tags=None, taggings=None):
        """
        Loads data from `filepath`.
        """
        self.geoindex = geoindex.GeoGridIndex(precision=4)
        tagindex = {}
        taggingsindex = {}

        if tags and taggings:
            for tag in load_data(tags):
                tagindex[tag['id']] = tag['tag']

            for tagging in load_data(taggings):
                shop_id = tagging['shop_id']
                tag_id = tagging['tag_id']
                tag_name = tagindex[tag_id]

                if shop_id not in taggingsindex:
                    taggingsindex[shop_id] = []
                taggingsindex[shop_id].append(tag_name)

        for shop in load_data(shops):
            shop['lat'] = float(shop['lat'])
            shop['lng'] = float(shop['lng'])
            shop['tags'] = taggingsindex.get(shop['id'], [])

            self[shop['id']] = shop

            self.geoindex.add_point(
                geoindex.GeoPoint(
                    shop['lat'],
                    shop['lng'],
                    ref=shop
                )
            )

    def shops_within_radius(self, lat, lng, radius, tags=None):
        """
        Searches shops within `radius`.
        `tags` should be a list of tag names, it will find shops
        that has *any* of the tags defined.
        Returns a generator of shops.
        """
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
            return tags_filter(get_shops())
        else:
            return get_shops()


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

    def products_in_shops(self, shops):
        """
        Gets all the products inside `shops`.
        `shops` needs to be an iterable with of dicts which contain
        the shop id as key. `shop = {'id': 'eiowfh33flj...'}`.
        Returns a generator of products.
        """
        for shop in shops:
            for product in self[shop['id']]:
                product['shop'] = shop
                yield product


def load_data(filepath):
    """
    Loads data from a csv file and yields dicts for each row.
    """
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row
