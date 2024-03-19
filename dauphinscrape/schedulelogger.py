import logging

from twisted.internet import task
from scrapy import signals
from scrapy.crawler import CrawlerRunner


class SchedulerQueueLogger:

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger("SchedulerQueueLogger")

        # Connect the engine_started method to the engine_started signal
        crawler.signals.connect(self.engine_started, signals.engine_started)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your extension object
        return cls(crawler)

    def engine_started(self):
        # This method is called once the Scrapy engine has started
        scheduler = self.crawler.engine.slot.scheduler

        # Use Twisted's task.LoopingCall to create a periodic task
        loop = task.LoopingCall(self.log_queue_size, scheduler)
        # Start the periodic task, call log_queue_size every 10 seconds
        loop.start(10)

    def log_queue_size(self, scheduler):
        # This method logs the current size of the scheduler queue
        try:
            queue_size = len(scheduler)
            self.logger.info(f"Current queue size: {queue_size}")
        except Exception as e:
            self.logger.error(f"Error logging queue size: {e}")
