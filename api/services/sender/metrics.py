from prometheus_client import Counter, Info

info = Info(name='mailing_service_metrics', documentation='')
info.info({'version': '1.0', 'language': 'python', 'framework': 'fastapi'})

mailouts_total_created = Counter(
    name='mailouts_total_created',
    documentation='Total number of mailouts created',
)

customers_total_created = Counter(
    name='customers_total_created',
    documentation='Total number of customers created',
)

messages_total_sent = Counter(
    name='messages_total_sent',
    documentation='Total number of messages successfully sent per mailout id',
)

messages_total_failed = Counter(
    name='messages_total_failed',
    documentation='Total number of messages failed (after a number of retries) per mailout id',
)
