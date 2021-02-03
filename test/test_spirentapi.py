from spirentapi import *

def test_demo():
    api = SpirentAPI()

    api.stc_connect('10.182.32.138')
    
    project = api.stc_create(objectType='Project', under='system1')

    api.stc_perform(cmd='SaveAsXml', config=project, filename='test.xml')

    api.stc_disconnect('10.182.32.138')