import pytest
from spirentapi import *

def test_stc():
    api = SpirentAPI()

    api.stc_connect('10.182.32.138')
    
    project = api.stc_create(objectType='Project', under='system1')

    assert project == 'project1'

    api.stc_perform(cmd='SaveAsXml', config=project, filename='test.xml')

    api.stc_disconnect('10.182.32.138')

def test_sth():
    api = SpirentAPI()

    conn_ret = api.sth_connect(device='10.182.32.138', port_list='1/1', break_locks=1)

    assert conn_ret.status == 1
    
    api.sth_cleanup_session()

def test_eval():
    api = SpirentAPI()

    assert api.eval('puts $tcl_version') == '8.5'

    del api

def test_normal_install():
    api = SpirentAPI()

    api.install('Tclx')

    del api

@pytest.mark.xfail(raises=RuntimeError)
def test_abnormal_install():

    api = SpirentAPI()
    api.install('FOO')

    del api