import os
import uuid
import json

from flask import Flask, request, jsonify, abort
import redis

from redis.exceptions import ConnectionError
from schematics.types import IntType, StringType, FloatType
from schematics.types.compound import ModelType, ListType
from schematics.models import Model
from schematics.exceptions import ModelValidationError

app = Flask(__name__)

REDIS_HOST = os.environ.get('DB_PORT_6379_TCP_ADDR')

"""
> 8 persons, add $4,320 for each additional person.
1 	$12,140
2 	$16,460
3 	$20,780
4 	$25,100
5 	$29,420
6 	$33,740
7 	$38,060
8 	$42,380
"""
POVERTY_LEVELS = {1: 12140, 2: 16460, 3: 20780, 4: 25100, 5: 29420,
                  6: 33740, 7: 38060, 8: 42380}
ADDITIONAL_SUM = 4320


class User(Model):
    age = IntType(required=True)
    gender = StringType(required=True, choices=['male', 'female'])


class Household(Model):
    members = ListType(ModelType(User), required=True, min_size=1)
    income = FloatType(required=True)


def get_redis_connection(host=REDIS_HOST):
    return redis.StrictRedis(host)


@app.route('/household/', methods=['POST'])
def new_household():
    try:
        db = get_redis_connection()
        payload = request.get_json()
        household = Household(payload)
        household.validate()
        data = json.dumps(household.to_primitive())
        id = str(uuid.uuid4())
        db.set(id, data)
        return jsonify(id), 200
    except ModelValidationError:
        abort(400, 'Validation Error')
    except ConnectionError:
        abort(404, 'Service is down')


@app.route('/household/<uuid:id>/', methods=['GET'])
def get_household(id):
    try:
        db = get_redis_connection()
        data = json.loads(db.get(id))
        return jsonify(data), 200
    except ConnectionError:
        abort(404, 'Service is down')


@app.route('/household/<uuid:id>/fpl-percent/', methods=['GET'])
def get_household_fpl(id):
    try:
        db = get_redis_connection()
        data = json.loads(db.get(id))
        household = Household(data)
        household_num = len(household.members)
        percent = 0
        fpl_sum = 0
        if household_num > 0:
            fpl_sum = POVERTY_LEVELS.get(household_num, POVERTY_LEVELS[8])
            if household_num > 8:
                for i in range(8, household_num):
                    fpl_sum = fpl_sum + ADDITIONAL_SUM
            percent = household.income / fpl_sum
        return jsonify(percent)
    except Exception:
        abort(404, 'Error')
    except ConnectionError:
        abort(404, 'Service is down')


@app.route('/sample-household/', methods=['GET'])
def get_sample_household():
    """ Retrieves a static, sample household object

    This route exists to demonstrate the schema for a Household object.
    It does not touch Redis.
    """
    sample_household = Household({
        'income': 50000,
        'members': [
            {'age': 45, 'gender': 'female'},
            {'age': 40, 'gender': 'male'},
        ],
    })

    return jsonify(sample_household.to_primitive()), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
