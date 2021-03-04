'''
Spirent TestCenter Object
'''

import logging
import re
from typing import Any, NoReturn, Union

from .apiwrapper import SpirentAPI, TCLWrapperError
from .tclwrapper import nested_list_to_tclstring

logger = logging.getLogger(__name__)

class STCObject:
    """STC Object

    STCObject is used to wrap STC object handle.
    with STCObject, you can access or set object's attribute by [ ] 
    """

    @staticmethod
    def create(type:str, **kwargs):
        """create STC Object

        Args:
            type (str): object type
            under (Optional, STCObject): STCObject under which will create the object
        """

        logger.info('create STCObject')

        # create Object
        handle = SpirentAPI.instance.stc_create(type, **kwargs)
        
        # wrap handle with STCObject
        return STCObject(handle)

    @staticmethod
    def is_handle(handle:str) -> bool:
        """check if handle str is SpirentTestCenter Object

        Args:
            handle (str): a possible handle str

        Returns:
            bool: True, it's SpirentTestCenter Object; False, not 
        """

        try:

            SpirentAPI.instance.stc_get(handle)

        except TCLWrapperError as e:

            logger.info('is_handle(%s):F' % handle)
            return False
        
        logger.info('is_handle(%s):T' % handle)

        return True

    def __init__(self, handle:str) -> None:
        """init function

        Args:
            type (ObjectType): ObjectType
        """

        logger.info('init STCObject %s' % handle)

        assert STCObject.is_handle(handle), '\'%s\' is invalid handle' % handle

        self._handle = handle

    @property
    def active(self) -> str:
        """active states

        Returns:
            str: 'true', for active; 'false', for unactive
        """
        return self['active']
    
    @active.setter
    def active(self, state:str) -> NoReturn:
        """set active state

        Args:
            state (str): state to set, 'true' or 'false'
        """
        if state.lower() not in ['true', 'false']:
            raise ValueError('state should be \'true\' or \'false\'')\
        
        self['active'] = state.lower()

    @property
    def name(self) -> Union[str, None]:
        """Object Name

        Returns:
            str: if it has a name ,return name str, else raise AttributeError
        """

        if 'Name' in self.attributes:

            return self['name']
        
        return None

    @name.setter
    def name(self, v:str) -> NoReturn:
        """set Object name

        Args:
            v (str): name to set
        """
        self['Name'] = v

    @property
    def type(self)-> str:
        """Object Type

        Returns:
            str: type of object
        """
        # bug fix:
        # use a new way to find type
        # 1. find parent
        # 2. try to create object by using handle name until success
        parent = self.parent
        index = -1
        while True:
            guess_type = self.handle[:index]
            if guess_type == '':
                break

            guess_handle = None
            try:
                guess_handle = SpirentAPI.instance.stc_create(guess_type, under=parent)
            except TCLWrapperError as error:
                pass
            finally:
                if guess_handle != None:
                    try:
                        SpirentAPI.instance.stc_delete(guess_handle)
                    except TCLWrapperError as error:
                        pass
                    finally:
                        return guess_type
                else:
                    index = index - 1
        
        raise RuntimeError('can\'t find type for %s' % self.handle)

    @property
    def handle(self) -> str:
        """Spirent TestCenter handle

        Returns:
            str: Spirent TestCenter Handle
        """
        assert self._handle != None, 'handle has been released'

        assert STCObject.is_handle(self._handle), 'handle(%s) is not valid any more' % self._handle

        return self._handle
    
    @property
    def parent(self):
        """parent of STC object

        Returns:
            STCObject: parent STCObject or None
        """

        if 'parent' in self.attributes:

            return STCObject(self['parent'])

        else:    
            return None

    @property
    def children(self):
        """children of STC object

        Returns:
            list[STCObject]: children
        """
        if 'children' in self.attributes:

            return [ STCObject(handle)  for handle in re.compile('\s+').split(self['children']) ]
        
        else:
            return [ ]

    @property
    def attributes(self) -> list[str]:
        """attributes of object

        Returns:
            list[str]: attributes list
        """

        return list(SpirentAPI.instance.stc_get(self.handle).keys())
    
    def __setitem__(self, name:str, value:Any) -> NoReturn:
        """set attribute by dict way

        Args:
            name (str): attribute name without space in it
            value (Any): value to set
        """
        assert ' ' not in name, 'attribute name should not contain space'
        
        if type(value) != list:
            if type(value) == str and ' ' in value:
                # if type is str, and there is space in it, add { }
                SpirentAPI.instance.stc_config(self.handle, **{name: "{%s}" % value})
            else:
                # other situations
                SpirentAPI.instance.stc_config(self.handle, **{name: "%s" % value})
        else:
            # if type is list, expand list
            SpirentAPI.instance.stc_config(self.handle, **{name: "%s" % nested_list_to_tclstring(value)})

    def __getitem__(self, name:str) -> Any:
        """get attribute by dict way

        Args:
            name (str): attribute name
        """
        return SpirentAPI.instance.stc_get(self.handle, [name])

    def __str__(self) -> str:
        """override __str__ to print handle name

        Returns:
            str: handle name
        """
        return self.handle
    
    def delete(self) -> NoReturn:
        """delete STCObject handle
        """
        if self.handle != None:
            SpirentAPI.instance.stc_delete(self.handle)
            self._handle = None