import pytest
from spirentapi import *

def test_stc():
    api = SpirentAPI()

    api.stc_connect('10.182.32.138')
    
    project = api.stc_create(objectType='Project', under='system1')

    assert project == 'project1'

    api.stc_perform(cmd='SaveAsXml', config=project, filename='test.xml')

    api.stc_disconnect('10.182.32.138')

def test_stc_exception():

    api =SpirentAPI()

    try:

        api.stc_get('sys')

    except TCLWrapperError as e:

        return
    
    assert False

def test_stc_get():

    api = SpirentAPI()

    d = api.stc_get('system1')
    
    for k in d.keys():
        print('--%s--' % k)
        print(api.stc_get('system1', attributes=[k]))

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

def test_abnormal_install():

    api = SpirentAPI()

    try:
        api.install('FOO')
    except RuntimeError as e:
        return

    assert False

def test_get_None():

    api = SpirentAPI()
    assert api.stc_get('system1.PhysicalChassisManager', ['children-PhysicalChassis']) == None

def test_singleton():

    api = SpirentAPI.instance
    api.x = 1
    api2 = SpirentAPI.instance
    assert api2.x == 1