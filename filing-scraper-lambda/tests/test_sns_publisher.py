import unittest
from unittest import mock

class SNSPublisherTest(unittest.TestCase):
    def test_sns_publisher_instance(self):
        from filing_scraper.sns_publisher import SNSPublisher
        inst = SNSPublisher()
        assert inst is not None
        assert isinstance(inst, SNSPublisher)
    
    @mock.patch('filing_scraper.sns_publisher.SNSPublisher.publish_email')
    def test_sns_publisher_publish(self, mock_sns_client):
        from filing_scraper.sns_publisher import SNSPublisher
        inst = SNSPublisher()
        mock_sns_client.return_value = None
        self.assertTrue(inst.publish_email("test_subj", "test_msg") is None)
        