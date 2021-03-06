import os
from ees.handlers.version import VersionHandler
from ees.handlers.commit import CommitHandler
from ees.handlers.invalid import InvalidEndpointHandler
from ees.handlers.changesets import FetchChangesetsHandler
from ees.handlers.events import FetchEventsHandler
from ees.handlers.global_changesets import FetchGlobalChangesetsHandler
from ees.handlers.global_indexer import GlobalIndexer
from ees.handlers.stats import StatsHandler
from ees.infrastructure.dynamodb import DynamoDB
from ees.commands import *

db = DynamoDB(events_table=os.getenv('EventStoreTable'),
              analysis_table=os.getenv('AnalysisTable'))


def route_request(cmd):
    commit = CommitHandler(db)
    version = VersionHandler()
    stats = StatsHandler(db)
    changesets = FetchChangesetsHandler(db)
    events = FetchEventsHandler(db)    
    global_changesets = FetchGlobalChangesetsHandler(db)
    invalid = InvalidEndpointHandler()
    global_indexer = GlobalIndexer(db)

    if isinstance(cmd, Version):
        return version
    
    if isinstance(cmd, Stats):
        return stats

    if isinstance(cmd, Commit):
        return commit
    
    if isinstance(cmd, FetchStreamChangesets):
        return changesets

    if isinstance(cmd, FetchStreamEvents):
        return events
    
    if isinstance(cmd, FetchGlobalChangesets):
        return global_changesets
    
    if isinstance(cmd, AssignGlobalIndexes):
        return global_indexer
    
    return invalid
