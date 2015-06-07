# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from . import models

import operator


api = Blueprint('api', __name__)

# These gets loaded when the api blueprint is registered in the app.
# They will live in memory until the app is shut down or restarted.
shopindex = None
productindex = None


@api.record_once
def load_data(setup_state):
    """
    Load the data for shops and products when this Blueprint is loaded.
    """
    global shopindex
    global productindex

    def data_path(filename):
        data_path = setup_state.app.config['DATA_PATH']
        return '{}/{}'.format(data_path, filename)

    shopindex = models.ShopIndex(
        shops=data_path('shops.csv'),
        tags=data_path('tags.csv'),
        taggings=data_path('taggings.csv')
    )
    productindex = models.ProductIndex(
        filepath=data_path('products.csv')
    )


@api.route('/search', methods=['GET'])
def search():
    """
    Searches for products.
    GET
    Available params are:
        lat
        lng
        radius - in kilometers
        limit - limits the amount of products returned
        tags - a comma seperated list of tag names "tag1,tag2,tag3"
    Returns:
        {
            "products": [{
                "id": "71b391298eea4451858a26fff62f1ca1",
                "popularity": 0.856,
                "quantity": 6,
                "shop_id": "96f7561caf784fa5a1593510ff0e7020",
                "title": "Serpico"
                "shop": {
                    "distance": 1.0709566864452733,
                    "id": "96f7561caf784fa5a1593510ff0e7020",
                    "lat": 59.357167770263686,
                    "lng": 17.926230931787334,
                    "name": "Osinski-Collins",
                    "tags": [
                        "shirts",
                        "accessories"
                    ]
                },
            },
            ...
            ]
        }
    """
    lat = float(request.args.get('lat', 0))
    lng = float(request.args.get('lng', 0))
    radius = float(request.args.get('radius', 2))
    limit = int(request.args.get('limit', 50))
    tags = request.args.get('tags', None)

    if tags:
        tags = tags.split(',')

    shops = shopindex.shops_within_radius(lat=lat, lng=lng, radius=radius, tags=tags)
    products = productindex.products_in_shops(shops)

    products = sorted(products, key=operator.itemgetter('popularity'), reverse=True)[:limit]

    return jsonify({
        'products': products
    })
