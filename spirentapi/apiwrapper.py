'''
Spirent TestCenter High Level Test API
'''
import logging
import os
import re
import shutil
from typing import Optional, Union, Any, NoReturn
from datetime import datetime

from .tclwrapper import *
from .utils import *

# logging
logger = logging.getLogger(__name__)

# Check Tcl/Tk Setting
TCLSHDIR = shutil.which('tclsh')
assert TCLSHDIR != None, 'Please install Tcl/Tk 8.5(https://www.activestate.com/products/tcl/downloads/) and add it in the PATH environment variable'

# Check Spirent TestCenter Installation
SPIRENTTESTCENTERDIR = os.getenv('SpirentTestCenter', None)
assert SPIRENTTESTCENTERDIR != None, 'Please setup the environment variable SpirentTestCenter, and point it to the SpirentTestCenter installation directory'
assert os.path.exists(os.path.join(SPIRENTTESTCENTERDIR, 'TestCenter.exe')), 'Please setup the SpirentTestCenter environment variable to the parent directory of TestCenter.exe'


class SpirentAPIMeta(type):

    def __init__(cls, *args, **kwargs) -> NoReturn:
        cls._instance = None
    
    @property
    def instance(cls):
        if cls._instance == None:
            cls._instance = SpirentAPI()
        
        return cls._instance


class SpirentAPI(metaclass=SpirentAPIMeta):
    """
    Spirent TestCenter API
    """
    
    def __init__(self) -> NoReturn:
        """HLTAPI initialization function

        Raises:
            TCLWrapperInstanceError: if start tclsh, raise this error
        """
        # initializate tclsh
        logger.info('start tcl process')
        self._tclsh = TCLWrapper(TCLSHDIR)
        self._tclsh.start()

        # install required Tclx, ip
        self.install("Tclx")
        self.install("ip")

        # init Spirent TestCenter Library
        logger.info('lappend auto_path {%s}' % SPIRENTTESTCENTERDIR)
        self._tclsh.eval('lappend auto_path {%s}' % SPIRENTTESTCENTERDIR)

        # load SpirentTestCenter, stc::
        logger.info('package require SpirentTestCenter')
        self._tclsh.eval('package require SpirentTestCenter')
            
        # load SpirentHltApi, sth::
        logger.info('package require SpirentHltApi')
        self._tclsh.eval('package require SpirentHltApi')

        # dynamically make sth:: function
        self._make_sth_func()
    
    def __del__(self) -> NoReturn:
        """shut down tcl process

        """
        logger.info('shutdown tcl process')
        if self._tclsh != None:          # stop Tcl shell
            self._tclsh.stop()
            self._tclsh = None
            logger.info('tclsh process stopped')

    def install(self,  package_name:str) -> NoReturn:
        """check if package is installed, if not, install it

        Args:
            package_name (str): package name to check and install , case-sensitive

        Raises:
            RuntimeError: if installation failed, raise RuntimeError
        """
        assert self._tclsh != None , "tcl is not started, can't check and install package"

        assert type(package_name) == str, 'package_name should be str type'

        logger.info('check and install package: %s'  % package_name)

        try:

            self._tclsh.eval(
                'if {[ catch { package require %s } error ]} { \
                    if {[ catch { teacup install %s } error2 ]}  { \
                        exit \
                    } \
                }' % (package_name, package_name))

        except TCLWrapperInstanceError as e:

            logger.critical(e)
            errorMsg = "fail to install package: %s(GFW will prevent you installing packages by TEACUP)" % package_name
            
            logger.critical(errorMsg)
            raise RuntimeError(errorMsg)

    def eval(self, cmd: Union[str,list[str]]) -> Union[str, list[str]]:
        """run tcl shell command, return the result

        Args:
            cmd (str or list[str]): cmd or cmd list to run

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError

        Returns:
            str or list[str]: result of str type or list[str] type
        """
        assert self._tclsh != None, "tcl is not started, can't check and install package"

        # delegates calls to TclWrapper
        if type(cmd) == list:

            # if command is list type, run command one by one
            ret = [ ]
            for c in cmd:

                assert type(c) == str, "command in list must be str type"

                logger.info(c)
                ret_ = remove_empty_lines(self._tclsh.eval(c))
                
                logger.debug(ret_)
                ret.append(ret_)
            
            return ret

        elif type(cmd) == str:

            # if command is str type, run command directly
            logger.info(cmd)
            ret = remove_empty_lines(self._tclsh.eval(cmd))

            logger.debug(ret)
            return ret

        else:
            # esle raise TypeError
            raise TypeError("cmd should be str or list[str] type")

    def _get_unique_name(self, name:str, start_index:Optional[int]=0):
        """return a unique variable name for name

        Args:
            name (str): name used to create unique variable name
            start_index (int, optional): suffix of unique name, default is 0
        
        Returns:
            str: unique name
        """
        if '_count' not in dir(self):
            self._count = { }
        
        # if name has a number suffix, strip off number suffix in the tail
        match = re.match('(^[\_a-zA-Z]+)(\d+$)', name)
        if match and len(match.groups()) == 2:
            name = match.groups()[0]
        
        if name not in self._count.keys():
            unique_name = '%s%d' % (name, start_index)
            self._count[name] = start_index + 1
        else:
            unique_name ='%s%d' % (name, self._count[name])
            self._count[name] = self._count[name] + 1
        
        # I don't verify if the name which I give is unique
        return unique_name

    def _run_api(self, variable:str, cmd:str, **kargs) -> dotdict:
        """run hlt api(sth::) and save the result to given variable, and automatically parse the result and save into a dot-accessible dict

        Args:
            variable (str): the variable to save
            cmd (str): sth:: cmd to run
            kargs (optional): argument passed to sth:: cmd

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError

        Returns:
            dotdict: a dot-accessible dict. there is a special key named name save the variable name, you can use this variable to access the result too
        """

        assert self._tclsh != None , "tcl is not started"
        
        assert type(variable) == str, 'variable should be str type'
        assert type(cmd) == str, 'cmd should be str type'

        # convert arguments
        args = dict_to_opt(kargs, prefix='-')
        
        
        # run command
        unique_name = self._get_unique_name(variable)
        cmd = 'set %s [ %s %s ]' % (unique_name, cmd, args)
        self.eval(cmd)

        # parse result data
        ret = self._resolve_keyset(unique_name)
        ret.name = unique_name

        # check result
        assert 'log' not in ret, ret.log

        return ret
    
    def _resolve_keyset(self, var:str, key:Optional[str]=None) -> Union[Any, dotdict]:
        """parse the result data of sth::

        Args:
            var (str): variable name
            key (str, optional): key, default is None，when None, it will access keys of var by keylkeys command
        
        Returns:
            dotdict or Any: if var is keyset, return dotdict which contains result, or if var is key, return value
        """
        key = '' if key == None else key
        if key.startswith('.'):
            key = key[1:]

        try:
            ret = dotdict()
            for sub_key in re.compile('\s+').split(self.eval('keylkeys %s %s' % (var, key))):
                ret[sub_key] = self._resolve_keyset(var, key = '%s.%s' % (key, sub_key))
            
            return ret

        except TCLWrapperError as error:

            return self.eval('keylget %s %s' % (var, key))

    def _make_sth_func(self) -> NoReturn:
        """dynamically create function
        
        for example:
            create sth_test_config for sth::test_config
            create stc_get for stc::get
        """
        
        def filter_func(api):
            return api.startswith('sth::')

        api_file_path = os.path.join(os.path.dirname(__file__), 'API.TXT')

        api_list = list(filter(filter_func, read_list(api_file_path)))
        
        # function name re
        api_exp = re.compile('(sth)::(.+$)')

        for api in api_list:

            logger.debug('create function: %s' % api)

            match = api_exp.match(api)
            assert match != None, 'only support sth:: api: %s' %  api
            
            prefix = match.groups()[0].strip()
            brief_name = match.groups()[1].strip()

            full_name = api.replace('::', '_')

            if getattr(SpirentAPI, full_name, False):
                logger.debug('%s already exists, skip' % full_name)
                continue

            setattr(SpirentAPI, full_name, eval("lambda self, **kargs : self._run_api('%s', '%s', **kargs)" % (brief_name, api)))

    def sth_connect(self, **kwargs):
        """sth::connect function

        Args:
            device (str): Spirent Test Center IP Address
            port_list (str): The port list to reserve. for example, { 1/8 1/9 }
            offline (int): 1, for offline port; 0, for online port
            break_locks (int): 1， break locks; 0, don't break locks

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError

        Returns:
            dotdict: a dotdict which can be accessible by dot way. there is a special port_handles key in the dict
        """
        assert type(kwargs) == dict


        ret = self._run_api('connect', 'sth::connect', **kwargs)

        ret.port_handles =  [ ]
        for port in re.split("\s+", kwargs['port_list']):
            port_handle = self.eval( 'keylget %s port_handle.%s.%s' % (ret.name, kwargs['device'], port))
            ret.port_handles.append(port_handle)
        
        logger.debug('sth_connect return: %s' % ret)
        return ret

    def stc_apply(self) -> NoReturn:
        """stc::apply

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        self.eval('stc::apply')
    
    def stc_config(self, handle:str, **kwargs) -> NoReturn:
        """stc::config

        Args:
            handle (str): handle or DDNPath

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(handle) == str, 'handle should be str type'

        self.eval('stc::config %s %s' % (handle, dict_to_opt(kwargs, prefix='-')))

    def stc_connect(self, chassisIp:str) -> NoReturn:
        """stc::connect

        Args:
            chassis_ip (str): chassis ip address

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(chassisIp) == str, 'chassisIp should be str type'

        self.eval('stc::connect %s' % chassisIp)

    def stc_create(self, objectType:str, **kwargs) -> str:
        """stc::create

        Args:
            objectType (str):  object type to create
            under (optional, str): parent handle

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError

        Returns:
            str: created object handle
        """
        assert type(objectType) == str, 'objectType should be str type'
        
        return self.eval('stc::create %s %s' % (objectType, dict_to_opt(kwargs, prefix='-')))

    def stc_delete(self, handle:str) -> NoReturn:
        """stc::delete

        Args:
            handle (str): handle to delete

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(handle) == str, 'handle should be str type'

        self.eval('stc::delete %s' % handle)

    def stc_disconnect(self, chassisIp:str) -> NoReturn:
        """stc::disconnect

        Args:
            chassisIp (str): chassis ip address

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(chassisIp) == str, 'chassisIp should be str type'

        self.eval('stc::disconnect %s' % chassisIp)

    def stc_get(self, handle:str, attributes:Optional[list[str]]=[]) -> Union[dotdict, str, int, float, bool, datetime]:
        """stc::get

        Args:
            handle (str): handle or DDNPath
            attributes (optional, list[str]): attributes to get
        
        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(handle) == str, 'data should be str type'

        attributes_str = ''

        for attribute in attributes:
        
            attributes_str = attributes_str + '-%s ' % attribute
        
        attributes_str = attributes_str.strip()

        result = self.eval('stc::get %s %s' % (handle, attributes_str))

        if len(attributes) != 1:

            return self._resolve_pairs(result)

        else:
            # if get only one attribute

            return result.strip()

    def _resolve_pairs(self, data:str) -> dotdict:
        """parse name-value pairs

        Args:
            data (str): string contains name-value

        Returns:
            dotdict: dict that contains name-value
        """
        assert type(data) == str, 'data should be str type'

        pair_re = re.compile('\s?-([\w\d\-\.]+)\s((\{[^{}]+\})|([\S]+))\s?')

        ret = dotdict()

        for t in pair_re.findall(data):

            key, val, _, _ = t

            if val.startswith('{') and val.endswith('}'):
            
                val = val[1:-1].strip()
        
            ret[key] = val
        
        return ret

    def stc_help(self, arg:str=None) -> str:
        """stc::help

        Args:
            arg (str, optional): None(default), commands, command, handle or objectType

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError

        Returns:
            str: help output
        """
        if arg != None:
            assert type(arg) == str, 'arg should be str type'

        return remove_empty_lines(self.eval('stc::help %s' % arg if arg != None else ''))

    def stc_help_list(self, configTypes_or_commands:str, pattern:str='') -> str:
        """stc::help list

        Args:
            configTypes_or_commands (str, optional): configTypes or commands
            pattern (str, optional): used to filter out configTypes or commands, default empty

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError

        Returns:
            str: help output
        """
        assert type(configTypes_or_commands) == str, 'configTypes_or_commands should be str type'
        assert configTypes_or_commands.lower() in ['configtypes', 'commands'], 'configTypes_or_commands should be configTypes or commands'

        assert type(pattern) == str, 'pattern should be str type'

        return remove_empty_lines(self.eval('stc::help list %s %s' % (configTypes_or_commands, pattern)))
    
    def stc_log(self, level:str, message:str) -> NoReturn:
        """stc::log

        Args:
            level (str): INFO, WARN, ERROR, FATAL
            message (str): message to log

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(level) == str, 'level should be str type'
        assert level.lower() in ['info', 'warn', 'error', 'fatal'], 'level should be one of INFO, WARN, ERROR, FATAL'

        assert type(message) == str, 'message should be str type'

        self.eval('stc::log %s "%s"' % (level, message))
    
    def stc_perform(self, cmd:str, **kwargs) -> NoReturn:
        """stc::perform

        Args:
            cmd (str): cmd to perform

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(cmd) == str, 'cmd should be str type'

        result = self.eval('stc::perform %s %s' % (cmd, dict_to_opt(kwargs, prefix='-')))

        return self._resolve_pairs(result)

    def stc_release(self, location:str) -> NoReturn:
        """stc::release

        Args:
            location (str): c/s/p, or //c/s/p

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(location) == str, 'location should be str type'

        self.eval('stc::release %s' % location)
    
    def stc_reserve(self, location:str) -> NoReturn:
        """stc::reserve

        Args:
            location (str): c/s/p, or //c/s/p

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(location) == str, 'location should be str type'

        self.eval('stc::reserve %s' % location)
    
    def stc_sleep(self, duration:int) -> NoReturn:
        """stc::sleep

        Args:
            duration (int): sleep duration

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(duration) == int, 'duration should be int type'

        self.eval('stc::sleep %s' % duration)
    
    def stc_subscribe(self, parent:str, configType:str, resultType:str, **kwargs) -> str:
        """stc::subscribe

        Args:
            parent (str): project handle
            configType (str): the possible configType objects are the ResultParent elements identified in the ResultChild relation defined for the results object
            resultType (str): specifies a results object type. The results object type determines the set of results to be collected

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
  
        Returns:
            str: handle to a ResultDataSet object
        """
        assert type(parent) == str, 'parent should be str type'
        assert type(configType) == str, 'configType should be str type'
        assert type(resultType) == str, 'resultType should be str type'

        return self.eval('stc::subscribe -parent %s -configType %s -resultType %s %s' % (parent, configType, resultType, dict_to_opt(kwargs, prefix='-')))
    
    def stc_unsubscribe(self, parent:str) -> NoReturn:
        """stc::unsubscribe

        Args:
            parent (str):  handle for the ResultDataSet object

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        assert type(parent) == str, 'parent should be str type'

        self.eval('stc::unsubscribe %s' % parent)

    def stc_waitUntilComplete(self, timeout:Optional[int]=None) -> NoReturn:
        """stc::waitUntilComplete

        Args:
            timeout (Optional[int], optional): timeout in seconds. Defaults to None, wait until complete

        Raises:
            TCLWrapperError: if running scripts failed, raise TCLWrapperError
        """
        if timeout == None:

            self.eval('stc::waitUntilComplete')
        else:
            assert type(timeout) == int, 'timeout should be int type'

            self.eval('stc::waitUntilComplete -timeout %s' % timeout)