from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from exceptions import NotFoundError
from credentials import MONGODB_URI
import json


app = Flask(__name__)


# create json encoder to encode object ids
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


# insert single document into collection

@app.route('/api/insert_one', methods=['POST'])
def insert_one_document():
    """Inserts single document into mongodb database. Insertion document should be supplied as JSON"""

    document_to_insert = request.get_json()

    # expression that inserts document in document_to_insert to collection
    try:
        result = collection.insert_one(document_to_insert)
        document_id = result.inserted_id
        print(f'_id of inserted document: {document_id}')
        return jsonify({
            'status': 200,
            'message': 'Single document insertion successful',
            'data': {
                # to first encode as json, then load that json for better view
                '_id': json.loads(JSONEncoder().encode(document_id))
            }
        })
    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Could not insert document.',
            'data': {}
        })

# insert multiple documents into collection


@app.route('/api/insert_many', methods=['POST'])
def insert_many_documents():
    """Inserts multiple documents into mongodb database, insertion documents should be supplied as an array of JSON format"""

    documents_to_insert = request.get_json()

    # expression that inserts document in document_to_insert to collection
    try:
        result = collection.insert_many(documents_to_insert)
        document_ids = result.inserted_ids
        print(f'_ids of inserted document: {document_ids}')
        return jsonify({
            'status': 200,
            'message': 'Multiple documents insertion successful',
            'data': {
                'num_inserted': len(document_ids),
                '_ids': json.loads(JSONEncoder().encode(document_ids))
            }
        })
    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Could not insert documents.',
            'data': {}
        })

# find documents from collection


@app.route('/api/find', methods=['GET'])
def find_documents():
    """Finds multiple documents based on query, query should be provided in the json itself"""
    try:
        # finding multiple documents returns a cursor
        query = request.get_json()

        # if id field is supplied in query, then it is supplied as a string, so convert it to ObjectId
        if query.get('_id') is not None:
            query['_id'] = ObjectId(query['_id'])

        # cursor object is not json serializable
        cursor = collection.find(query)
        num_docs = 0
        return_data = []
        for document in cursor:
            num_docs += 1
            return_data.append(document)
        print('# of documents found: {}'.format(num_docs))
        return jsonify({
            'status': 200,
            'message': 'Finding documents successful',
            'data': {
                'num_docs': num_docs,
                'docs': json.loads(JSONEncoder().encode(return_data))
            }
        })
    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Problem occured while searching documents',
            'data': {}
        })

# update one document from collection


@app.route('/api/update_one', methods=['PUT'])
def update_one_document():
    """Updates single document based on query, and provided json update data. Query and update data should be provided in JSON format"""
    # provided update
    body = request.get_json()
    query = body["query"]

    # if _id is provided, it is provided as a string, so it must be changed to ObjectId type
    if query.get('_id') is not None:
        query['_id'] = ObjectId(query['_id'])

    update_content = body["update"]

    try:
        # try to find the document based on query
        document_to_update = collection.find_one(query)

        if document_to_update is None:
            raise NotFoundError
        # expression to update target based on query and update json
        result = collection.update_one(query, update_content)
        print('Documents updated: {}'.format(result.modified_count))

        return jsonify({
            'status': 200,
            'message': 'Single document update successful',
            'data': {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'document_before_update': json.loads(JSONEncoder().encode(document_to_update)),
                'document_after_update': json.loads(JSONEncoder().encode(collection.find_one(query)))
            }
        })
    except NotFoundError:
        return jsonify({
            'status': 404,
            'message': 'Error! Query does not match any document',
            'data': {}
        })

    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Could not update document',
            'data': {}
        })

# update many documents from collection


@app.route('/api/update_many', methods=['PUT'])
def update_many_documents():
    """Updates many documents based on search query and provided update data. Query and update data should be provided in JSON format"""
    # provided update
    body = request.get_json()
    query = body["query"]

    # if _id is provided, it is provided as a string, so it must be changed to ObjectId type
    if query.get('_id') is not None:
        query['_id'] = ObjectId(query['_id'])

    update_content = body["update"]

    try:
        # check if even a single document matching to query exists
        document_sample = collection.find_one(query)
        if document_sample is None:
            raise NotFoundError
        # expression for updating multiple users documents in collection
        result = collection.update_many(query, update_content)
        print('Matched count: {}'.format(result.matched_count))
        print('Modified count: {}'.format(result.modified_count))
        return jsonify({
            'status': 200,
            'message': 'Multiple documents update successful',
            'data': {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count
            }
        })
    except NotFoundError:
        return jsonify({
            'status': 404,
            'message': 'Error! Query does not match any document',
            'data': {}
        })

    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Could not update documents',
            'data': {}
        })

# delete one document from collection


@ app.route('/api/delete_one', methods=['DELETE'])
def delete_one_document():
    """Deletes one document from collection based on provided query, query should be provided in JSON"""

    query = request.get_json()

    # if _id is provided, it is provided as a string, so it must be changed to ObjectId type
    if query.get('_id') is not None:
        query['_id'] = ObjectId(query['_id'])

    try:
        # try to find out if the document exists
        document_to_delete = collection.find_one(query)

        if document_to_delete is None:
            raise NotFoundError
        # expression to delete single document from collection
        result = collection.delete_one(query)
        print('Deleted count: {}'.format(result.deleted_count))
        return jsonify({
            'status': 200,
            'message': 'Single document deletion successful',
            'data': {
                'deleted_count': result.deleted_count,
                'deleted_document': json.loads(JSONEncoder().encode(document_to_delete))
            }
        })

    except NotFoundError:
        return jsonify({
            'status': 404,
            'message': 'Error! Query does not match any document',
            'data': {}
        })

    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Could not delete documents',
            'data': {}
        })

# delete many documents from collection


@ app.route('/api/delete_many', methods=['DELETE'])
def delete_many_documents():
    """Deletes multiple documents from collection based on provided query. Query should be provided in JSON."""
    query = request.get_json()

    # if _id is provided, it is provided as a string, so it must be changed to ObjectId type
    if query.get('_id') is not None:
        query['_id'] = ObjectId(query['_id'])

    try:
        # check if even one document exists
        document_sample = collection.find_one(query)
        if document_sample is None:
            raise NotFoundError
        # expression to delete multiple documents from collection
        result = collection.delete_many(query)
        print('Documents deleted: {}'.format(result.deleted_count))
        return jsonify({
            'status': 200,
            'message': 'Deletion of multiple documents successful',
            'data': {
                'deleted_count': result.deleted_count
            }
        })
    except NotFoundError:
        return jsonify({
            'status': 404,
            'message': 'Error! Query does not match any document',
            'data': {}
        })

    except:
        return jsonify({
            'status': 404,
            'message': 'Error! Could not delete documents',
            'data': {}
        })


if __name__ == '__main__':
    client = MongoClient(MONGODB_URI)
    db = client.mini_project
    collection = db.users
    app.run(debug=True)
