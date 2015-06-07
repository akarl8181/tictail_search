import mock


class TestAPI(object):
    def test_search(self, get):
        with mock.patch.multiple(
                'server.api', shopindex=mock.DEFAULT, productindex=mock.DEFAULT
        ) as mocks:
            shops_within_radius = mocks['shopindex'].shops_within_radius
            products_in_shops = mocks['productindex'].products_in_shops

            products_in_shops.return_value = [
                {'id': 'product1', 'popularity': 0.4},
                {'id': 'product2', 'popularity': 0.8},
                {'id': 'product3', 'popularity': 0.2},
                {'id': 'product4', 'popularity': 0.9},
            ]

            shops_within_radius.return_value = [
                {'id': 'shop1'},
                {'id': 'shop2'},
                {'id': 'shop3'},
                {'id': 'shop4'},
            ]

            response = get('/search', query_string={
                'lat': 59.00,
                'lng':  18.00,
                'radius': 0.3
            })

            shops_within_radius.assert_called_once_with(
                lat=59.00,
                lng=18.00,
                radius=0.3,
                tags=None
            )

            assert list(products_in_shops.call_args[0][0]) == shops_within_radius.return_value
            assert response.json['products'][0] == products_in_shops.return_value[3]

    def test_limit(self, get):
        with mock.patch('server.api.productindex') as productindex:
            productindex.products_in_shops.return_value = [
                {'id': 'product1', 'popularity': 0.4},
                {'id': 'product2', 'popularity': 0.8},
                {'id': 'product3', 'popularity': 0.2},
                {'id': 'product4', 'popularity': 0.9},
            ]

            response = get('/search', query_string={
                'lat': 59.00,
                'lng':  18.00,
                'radius': 300,
                'limit': 2
            })

            assert 2 == len(response.json['products'])

    def test_sort(self, get):
        with mock.patch('server.api.productindex') as productindex:
            productindex.products_in_shops.return_value = [
                {'id': 'product1', 'popularity': 0.4},
                {'id': 'product2', 'popularity': 0.8},
                {'id': 'product3', 'popularity': 0.2},
                {'id': 'product4', 'popularity': 0.9},
            ]

            response = get('/search', query_string={
                'lat': 59.00,
                'lng':  18.00,
                'radius': 3,
                'limit': 2
            })

            assert response.json['products'][0] == productindex.products_in_shops.return_value[3]

    def test_tags(self, get):
        with mock.patch('server.api.shopindex') as shopindex:
            get('/search', query_string={
                'tags': 'tag1,tag2,tag3'
            })

            shopindex.shops_within_radius.assert_called_once_with(
                lat=mock.ANY,
                lng=mock.ANY,
                radius=mock.ANY,
                tags=['tag1', 'tag2', 'tag3']
            )
