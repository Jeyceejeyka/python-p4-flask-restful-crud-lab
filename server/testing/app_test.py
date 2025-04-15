import json

from server.app import app  # Ensure the correct import path for `app`
from models import db, Plant

class TestPlant:
    '''Flask application in app.py'''

    def test_plants_get_route(self):
        '''has a resource available at "/plants".'''
        response = app.test_client().get('/plants')
        assert(response.status_code == 200)

    def test_plants_get_route_returns_list(self):
        '''returns JSON representing list of Plant objects at "/plants".'''
        response = app.test_client().get('/plants')
        data = json.loads(response.data.decode())

        assert(type(data) == list)
        assert(len(data) > 0)
        assert(all(type(item) == dict for item in data))
        assert(all("id" in item for item in data))

    def test_plants_post_route_creates_plant(self):
        '''can create new plant via POST at "/plants".'''
        response = app.test_client().post(
            '/plants',
            json={
                "name": "Test Plant",
                "image": "test.jpg",
                "price": 9.99,
                "is_in_stock": True
            }
        )
        data = json.loads(response.data.decode())

        assert(response.status_code == 201)
        assert(data["name"] == "Test Plant")
        assert(data["price"] == 9.99)

    def test_plant_by_id_404(self):
        '''returns 404 for non-existent plant at "/plants/<int:id>".'''
        response = app.test_client().get('/plants/9999')
        assert(response.status_code == 404)

    def test_plant_post_validation(self):
        '''returns 400 for invalid plant data at POST "/plants".'''
        response = app.test_client().post(
            '/plants',
            json={
                "name": "Invalid",
                # Missing required fields
            }
        )
        assert(response.status_code == 400)

    def test_plant_by_id_get_route(self):
        '''has a resource available at "/plants/<int:id>".'''
        response = app.test_client().get('/plants/1')
        assert(response.status_code == 200)

    def test_plant_by_id_get_route_returns_one_plant(self):
        '''returns JSON representing one Plant object at "/plants/<int:id>".'''
        response = app.test_client().get('/plants/1')
        data = json.loads(response.data.decode())

        assert(type(data) == dict)
        assert(data["id"])
        assert(data["name"])

    def test_plant_by_id_patch_route_updates_is_in_stock(self):
        '''returns JSON representing updated Plant object with "is_in_stock" = False at "/plants/<int:id>".'''
        with app.app_context():
            plant_1 = Plant.query.filter_by(id=1).first()
            plant_1.is_in_stock = True
            db.session.add(plant_1)
            db.session.commit()
            
        response = app.test_client().patch(
            '/plants/1',
            json = {
                "is_in_stock": False,
            }
        )
        data = json.loads(response.data.decode())

        assert(type(data) == dict)
        assert(data["id"])
        assert(data["is_in_stock"] == False)

    def test_plant_by_id_delete_route_deletes_plant(self):
        '''returns JSON representing updated Plant object at "/plants/<int:id>".'''
        with app.app_context():
            lo = Plant(
                name="Live Oak",
                image="https://www.nwf.org/-/media/NEW-WEBSITE/Shared-Folder/Wildlife/Plants-and-Fungi/plant_southern-live-oak_600x300.ashx",
                price=250.00,
                is_in_stock=False,
            )

            db.session.add(lo)
            db.session.commit()
            
            response = app.test_client().delete(f'/plants/{lo.id}')
            data = response.data.decode()

            assert(not data)