import boto3
from eb_sqs.settings import QUEUE_PREFIX, AUTO_ADD_QUEUE


class SqsClient:
    class QueueDoesNotExistException(Exception):
        def __init__(self, queue_name):
            super(SqsClient.QueueDoesNotExistException, self).__init__()
            self.queue_name = queue_name

    def __init__(self):
        self.sqs = boto3.resource('sqs')
        self.queue_cache = {}

    def _get_queue(self, queue_name):
        queue_name = '{}-{}'.format(QUEUE_PREFIX, queue_name)

        queue = self.queue_cache.get(queue_name, self.sqs.get_queue_by_name(QueueName=queue_name))
        if not queue:
            if AUTO_ADD_QUEUE:
                queue = self.sqs.create_queue(QueueName=queue_name)
                self.queue_cache[queue_name] = queue
            else:
                raise SqsClient.QueueDoesNotExistException(queue_name)

        return queue

    def add_message(self, queue_name, msg, delay):
        queue = self._get_queue(queue_name)
        queue.send_message(
            MessageBody=msg,
            DelaySeconds=delay
        )