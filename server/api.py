# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, jsonify, request
from . import models

import operator


api = Blueprint('api', __name__)

shopindex = None
productindex = None
tagindex = None


@api.record_once
def load_data(setup_state):
    global shopindex
    global productindex
    global tagindex

    def data_path(filename):
        data_path = setup_state.app.config['DATA_PATH']
        return '{}/{}'.format(data_path, filename)

    shopindex = models.ShopIndex(
        shops=data_path('shops.csv'),
        taggings=data_path('taggings.csv')
    )
    productindex = models.ProductIndex(
        filepath=data_path('products.csv')
    )
    tagindex = models.TagIndex(
        tags=data_path('tags.csv')
    )


@api.route('/search', methods=['GET'])
def search():
    lat = float(request.args.get('lat', 0))
    lng = float(request.args.get('lng', 0))
    radius = float(request.args.get('radius', 10)) / 1000  # We want radius in meters
    limit = int(request.args.get('limit', 5000))
    tags = request.args.get('tags', None)

    if tags is not None:
        tags = tags.split(',')

    shops = shopindex.shops_within_radius(lat=lat, lng=lng, radius=radius, tags=tags)
    products = productindex.products_in_shops(
        (shop['id'] for shop in shops)
    )

    products = sorted(products, key=operator.itemgetter('popularity'), reverse=True)[:limit]

    return jsonify({
        'count': len(products),
        'products': products
    })
