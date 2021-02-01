import json


class FetchChangesets:
    def __init__(self, db):
        self.db = db

    def execute(self, event, context):
        query_string = event.get("queryStringParameters") or {}
        stream_id = event["pathParameters"].get("stream_id")
        if not stream_id:
            return self.missing_stream_id()
        to_changeset = query_string.get("to")
        from_changeset = query_string.get("from")

        if to_changeset:
            try:
                to_changeset = int(to_changeset)
            except ValueError:
                return self.invalid_filtering_values_type(stream_id)
        
        if from_changeset:
            try:
                from_changeset = int(from_changeset)
            except ValueError:
                return self.invalid_filtering_values_type(stream_id)
        
        if to_changeset and from_changeset and from_changeset > to_changeset:
            return self.invalid_filtering_values(stream_id, from_changeset, to_changeset)

        changesets = self.db.fetch_stream_changesets(
            stream_id,
            from_changeset=from_changeset,
            to_changeset=to_changeset)

        changesets = [{ "changeset_id": c.changeset_id,
                        "events": c.events,
                        "metadata": c.metadata } for c in changesets]
        
        if not changesets:
            last_commit = self.db.fetch_last_commit(stream_id)
            if not last_commit:
                return self.stream_not_found(stream_id)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "stream_id": stream_id,
                "changesets": changesets
            }, indent=4),
        }
    
    def invalid_filtering_values_type(self, stream_id):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "stream_id": stream_id,
                "error": "INVALID_CHANGESET_FILTERING_PARAMS",
                "message": 'The filtering params(from_changeset, to_changeset) have to be integer values'
            })
        }
    
    def invalid_filtering_values(self, stream_id, from_changeset, to_changeset):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "stream_id": stream_id,
                "error": "INVALID_CHANGESET_FILTERING_PARAMS",
                "message": f'The higher boundary cannot be lower than the lower boundary: {from_changeset}(from) > {to_changeset}(to)'
            })
        }
    
    def missing_stream_id(self):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "MISSING_STREAM_ID",
                "message": 'stream_id is a required value'
            })
        }
    
    def stream_not_found(self, stream_id):
        return {
            "statusCode": 404,
            "body": json.dumps({
                "stream_id": stream_id,
                "error": "STREAM_NOT_FOUND",
                "message": f'The specified stream({stream_id}) doesn\'t exist'
            })
        }