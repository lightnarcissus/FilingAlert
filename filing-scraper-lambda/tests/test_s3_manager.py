import pytest

def test_s3_manager_instance():
    from filing_scraper.s3_manager import S3Manager
    inst = S3Manager()
    assert inst is not None
    assert isinstance(inst, S3Manager)