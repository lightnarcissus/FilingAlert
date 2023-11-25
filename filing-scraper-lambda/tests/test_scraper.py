import pytest

_MOCK_KEYS = ["test", "mock_key"]
_MOCK_SOURCES = ["{}", "{'test':'value'}"]


@pytest.fixture(params=_MOCK_KEYS)
def test_keys(request):
    return request.param


@pytest.fixture(params=_MOCK_SOURCES)
def test_sources(request):
    return request.param

def test_scraper_lambda_entrypoint():
    from filing_scraper import scraper
    assert(hasattr(scraper, 'main'))
    
def test_scraper_instance(test_keys, test_sources):
    from filing_scraper.scraper import FilingScraper
    inst = FilingScraper(key=test_keys, name="mock_instance", source=test_sources)
    assert inst is not None
    assert isinstance(inst, FilingScraper)
    assert inst.name == "mock_instance"
    assert inst.key == test_keys
    assert inst.source_dict == test_sources