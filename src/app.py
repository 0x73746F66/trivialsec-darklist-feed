import json
from datetime import datetime, timezone

from pydantic.error_wrappers import ValidationError

import internals
import config
import models
import services.aws


def pre_process(contents: str, category: str) -> list[models.Darklist]:
    internals.logger.debug("pre_process")
    results = []
    if not contents:
        return results
    for line in contents.splitlines():
        if line.startswith('#'):
            continue
        ip_address = line.strip()
        if not ip_address:
            continue
        try:
            if '/' in line:
                results.append(
                    models.Darklist(
                        cidr=line,
                        last_seen=datetime.now(timezone.utc),
                        category=category,
                    )
                )
            else:
                results.append(
                    models.Darklist(
                        ip_address=ip_address,
                        last_seen=datetime.now(timezone.utc),
                        category=category,
                    )
                )
        except ValidationError as err:
            internals.logger.warning(err, exc_info=True)
            internals.logger.warning(line)
    internals.logger.info(f"Parsed {len(results)} records")

    return results


def fetch(feed: models.FeedConfig) -> list[models.Darklist]:
    internals.logger.debug("fetch")
    if feed.disabled:
        internals.logger.info(f"{feed.name} [magenta]disabled[/magenta]")
        return []
    file_path = internals.download_file(feed.url)
    if file_path.exists():
        return pre_process(file_path.read_text(encoding='utf8'), feed.name)
    return []


def process(feed: models.FeedConfig, feed_items: list[models.Darklist]) -> list[models.FeedStateItem]:
    state = models.FeedState(source=feed.source, feed_name=feed.name)
    # initial ONLY block
    if not state.load():
        internals.logger.warning("process initial ONLY")
        state.url = feed.url
        state.records = {}
        for item in feed_items:
            if item.ip_address:
                state.records[str(item.ip_address)] = models.FeedStateItem(
                    key=str(item.ip_address),
                    data=item,
                    data_model='Darklist',
                    first_seen=item.last_seen,
                    current=True,
                    entrances=[],
                    exits=[],
                )
            if item.cidr:
                state.records[str(item.cidr)] = models.FeedStateItem(
                    key=str(item.cidr),
                    data=item,
                    data_model='Darklist',
                    first_seen=item.last_seen,
                    current=True,
                    entrances=[],
                    exits=[],
                )

    internals.logger.info("process exit records")
    feed_index = {str(feed_item.ip_address) for feed_item in feed_items}
    for state_item in state.records.keys():
        if state_item not in feed_index:
            state.exit(state_item)

    entrants = []
    internals.logger.info("process new entrants")
    for feed_item in feed_items:
        key = feed_item.cidr or feed_item.ip_address
        if item := state.records.get(str(key)):
            if item.current:
                continue
            item.current = True
            item.entrances.append(datetime.now(timezone.utc))
        else:
            item = models.FeedStateItem(
                key=str(key),
                data=feed_item,
                data_model='Darklist',
                first_seen=datetime.now(timezone.utc),
                current=True,
                entrances=[datetime.now(timezone.utc)],
                exits=[],
            )
        state.records[item.key] = item
        entrants.append(item)

    internals.logger.info("persist state")
    state.last_checked = datetime.now(timezone.utc)
    state.save()
    internals.logger.info(f"Detected {len(entrants)} new entrants")
    return entrants


def handler(event, context):
    start = datetime.now(timezone.utc)
    for feed in config.feeds:
        results = fetch(feed)
        if not results:
            continue
        # services.aws.delete_s3(f"{internals.APP_ENV}/feeds/{feed.source}/{feed.name}/state.json")
        services.aws.store_s3(
            path_key=f"{internals.APP_ENV}/feeds/{feed.source}/{feed.name}/{start.strftime('%Y%m%d%H')}.json",
            value=json.dumps(results, default=str)
        )
        for state_item in process(feed, results):
            services.aws.store_sqs(
                queue_name=f'{internals.APP_ENV.lower()}-early-warning-service',
                message_body=json.dumps({**feed.dict(), **state_item.dict()}, cls=internals.JSONEncoder),
                deduplicate=False,
            )
        internals.logger.debug(f"done {feed.name}")
