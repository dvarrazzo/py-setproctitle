def pytest_configure(config):
    config.addinivalue_line(
        "markers", "embedded: the test create an embedded executable"
    )
