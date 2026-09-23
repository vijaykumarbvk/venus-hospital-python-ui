"""
Circuit breaker (pybreaker) + event publishing.

Originally used Kafka + Zookeeper. Kafka is JVM software -- that's
inherent to Kafka itself, unrelated to this app being Python. Running
it well on Kubernetes brought a long tail of JVM-specific operational
friction (StatefulSet field immutability, the four-letter-word command
whitelist, zoo.cfg templating quirks, EBS AZ affinity) that has nothing
to do with this app's code.

Nothing in this codebase consumes these events yet -- every call site
is `event_publisher.publish(topic, key, event)` and nothing else reads
them back. That means the app needs a durable, ordered append log, not
Kafka's specific consumer-group/partition/rebalance machinery. Redis
Streams (XADD) gives the same semantics using infrastructure this
project already runs -- the same ElastiCache Redis instance backing
@cached and the API gateway's rate limiter. No JVM, no StatefulSet, no
PVC, nothing to fight.

publish(topic, key, event) keeps the exact signature the Kafka version
had, so no calling code in any service needs to change.
"""
import json
import logging
import os

import pybreaker
import redis

logger = logging.getLogger(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

# Cap each stream at ~10k entries (approximate trim -- cheap, doesn't
# require an exact count) so a topic nobody's consuming yet doesn't
# grow Redis's memory unbounded.
STREAM_MAXLEN = int(os.environ.get("EVENT_STREAM_MAXLEN", 10000))


def build_breaker(name: str, fail_max: int = 5, reset_timeout: int = 30) -> pybreaker.CircuitBreaker:
    """One shared breaker per outbound dependency; services call this to
    make a named breaker per downstream call (e.g. calls to user-service)."""
    return pybreaker.CircuitBreaker(
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        name=name,
    )


class EventPublisher:
    """Lazily-connected Redis Streams producer with graceful degradation."""

    def __init__(self):
        self._client = None

    def _get_client(self) -> "redis.Redis":
        if self._client is None:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
        return self._client

    def publish(self, topic: str, key, event: dict):
        """
        Append `event` to the Redis stream named `topic`. Redis Streams
        preserve insertion order per-stream and are durable (persisted
        with Redis's normal AOF/RDB persistence), same as a Kafka topic
        with a single partition -- which is all this app ever used.
        """
        try:
            client = self._get_client()
            fields = {
                "key": str(key) if key is not None else "",
                "payload": json.dumps(event, default=str),
            }
            client.xadd(topic, fields, maxlen=STREAM_MAXLEN, approximate=True)
        except redis.RedisError as exc:
            # Publishing failures should never break the primary request flow.
            logger.warning("Redis Streams publish failed for topic=%s: %s", topic, exc)


event_publisher = EventPublisher()
