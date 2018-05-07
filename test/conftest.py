import pytest
from wrangling import script_utils as scu


@pytest.fixture
def connection(mocker):
    return mocker.patch.object(scu.submit_utils, 'FDN_Connection')
