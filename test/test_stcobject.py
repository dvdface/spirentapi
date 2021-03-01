import pytest
from spirentapi import STCObject

def test_create():
    portObject = STCObject.create('port', under='project1')
    assert portObject.parent.handle == 'project1'

def test_is_handle():
    
    assert STCObject.is_handle('portx') == False

    portObject = STCObject.create('port', under='project1')

    assert STCObject.is_handle(portObject.handle)

def test_active():

    portObject = STCObject.create('port', under='project1')
    assert portObject.active == 'true'

    portObject.active = 'false'
    assert portObject.active == 'false'

def test_name():

    projectObject = STCObject.create('project')
    assert projectObject.name == 'Project 1'

    projectObject.name = 'xx'

    assert projectObject.name == 'xx'

def test_type():
    projectObject = STCObject.create('project')
    assert projectObject.type == 'project'

def test_handle():
    systemObject = STCObject('system1')
    assert systemObject.handle == 'system1'

def test_parent():
    systemObject = STCObject('system1')
    assert systemObject.parent == None

    projectObject = STCObject('project1')
    assert projectObject.parent.handle == 'system1'

def test_attributes():
    systemObject = STCObject('system1')
    assert 'Active' in systemObject.attributes
    assert 'Name' in systemObject.attributes
    assert 'Version' in systemObject.attributes
    assert 'children' in systemObject.attributes

def test_children():
    systemObject = STCObject('system1')
    rprObject = STCObject('resultproviderregistry1')
    print([ child.handle for child in rprObject.children])