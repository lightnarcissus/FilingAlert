import pytest


def test_sns_publisher_instance():
    from filing_scraper.sns_publisher import SNSPublisher
    inst = SNSPublisher()
    assert inst is not None
    assert isinstance(inst, SNSPublisher)