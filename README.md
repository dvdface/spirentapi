# changelist
* 1.4.6,  fix bug in STCObject attribute setting
* 1.4.5,  fix STCObject.type bug
* 1.4.2,  fix stc_get function to return None instead of '' str
* 1.4.1,  fix deadlock problem when output too many characters in stdout
* 1.4.0,  add STCObject, you can use this object to wrap handle return by stc_create, stc_get, then you can easily access and set attribute by object[attribute] way
* 1.3.1,  fix bug: some value is mask, such as 111, 011, should keep it str type, auto convert function can't deal with it, so remove auto convertion to result
* 1.3.0,  add singleton mode, you can use SpirentAPI.instance to get instance
* 1.2.7,  fix bug in stc::get
* 1.2.6,  add testcase
* 1.2.5,  strip space after strip { }; turn '' result to None
* 1.2.4,  add pytest-cov
* 1.2.3,  fix bug in stc_get
* 1.2.2,  fix bug in stc_get, stc_get(self, handle:str, attributes:Optional[list[str]]=[]) -> Union[dotdict, str, int, float, bool, datetime]
* 1.2.1,  add testcases
* 1.2.0,  change function signature to stc_get(self, handle:str, attributes:Optional[list[str]]=[]) -> dotdict:
* 1.1.0,  support convert true/false to bool type, and break children attribute's value to list
* 1.0.2,  fix missing API.TXT
* 1.0.1,  update brief
* 1.0.0,  support stc:: sth:: tclsh call

# feedback
* send email to dvdface@gmail.com
* visit https://github.com/dvdface/spirentapi

# how to install
`pip install spirentapi`

# known issues
* Greate FireWall in China may prevent teacup install Tclx and ip pakcages<br/>

Tclx and ip packages are needed by SpirentHltApi<br/>

so, you may need VPN to install Tclx and ip<br/>

you can try to type `teacup install Tclx` and `teacup install ip` in the tclsh to check<br/>

# how to use
1. **install Tcl/Tk<br/>**
   
   visit https://www.activestate.com/products/tcl/downloads/  to install Tcl/Tk<br/>

   Spirent TestCenter need 8.5 version<br/>
2. **set PATH environment<br/>**

   set `PATH` environment, include tcl/tk path <br/>

   for example:<br/>

   `PATH=C:\Tcl\bin;%PATH%`<br/>
3. **install Spirent TestCenter<br/>**

   visit Spirent TestCenter Web Portal, download and install Spirent TestCenter<br/>
4. **set SpirentTestCenter environment<br/>**

   set `SpirentTestCenter` environment<br/>

   point to Spirent TestCenter installation directory<br/>

   testcenter.exe should under the path<br/>

   for example:<br/>

      `SpirentTestCenter="C:\Program Files\Spirent Communications\Spirent TestCenter 4.95\Spirent TestCenter Application"`<br/>
5. **import spirentapi**
    ```
    from spirentapi import SpirentAPI
    ```
6. **use tclsh**
    ```
    # create SpirentAPI object
    api = SpirentAPI()
    
    # use teacup to install packages
    # you don't need install Tclx, ip, SpirentAPI's __init__ function will install for you
    api.install('Tclx') 
    api.install('ip')

    # run tcl/sh command
    # you don't need run the following commands, SpirentAPI's __init__ function will run for you
    api.eval('package require SpirentTestCenter')
    api.eval('package require SpirentHltApi')

    # shutdown tclsh
    del api
    ```
7. **use stc:: api**
    ```
    # create SpirentAPI object
    api = SpirentAPI()

    # call stc::connect
    api.stc_connect(chassisIp='10.182.32.138')
    
    # call stc::create, and access result
    project_handle = api.stc_create(objectType='Project', under='system1')

    # use STCObject to wrap handle to access or set attributes
    project_object = STCObject(project_handle)
    project_object['Name']
    project_object['Name'] = 'new name'
    
    # call stc::perform
    api.stc_perform(cmd='SaveAsXml', config=project_handle, filename='test.xml')
    
    # call stc::disconnect
    api.stc_disconnect(chassisIp='10.182.32.138')

    # shutdown tclsh
    del api
    ```
8. **use sth:: api**
   
   Notes: because sth:: function is dynamically created, so some IDE can't give you hint. If you know how to fix it, tell me(dvdface@hotmail.com)
    ```
    # create SpirentAPI object
    api = SpirentAPI()

    # call sth::connect -device '10.182.32.138' -port_list '1/1 1/11', and access result
    conn_ret = api.sth_connect(device='10.182.32.138', port_list='1/1 1/11', break_locks=1)
    
    # access result by dot
    # name is a special key, save the variable name of sth:: command returns
    # if you want to access the result by youself, you can use the variable
    conn_ret.name
    conn_ret.status
    conn_ret.offline
    
    # call sth::cleanup_session
    api.sth_cleanup_session()

    # shutdown tclsh
    del api
    ```
# how to extend
1. **override default implementation of sth::**<br/>
   Sometimes, it's not convenience to access result of sth:: command by dot<br/>

   for example:<br/>

   ```
   conn_ret = api.sth_connect(device='10.182.32.138', port_list='1/1 1/11', break_locks=1)

   # access port handle is very unconvenience
   conn_ret['port_handle']['10']['182']['32']['138']['1/1']

   # so you can extend SpirentAPI, add a sth_connect function to override dynamically created function
   class MyExtendedAPI(SpirentAPI):

      def sth_connect(self, **kwargs):

         # use _run_api to run sth::connect
         # same as set connect? [ sth::connect ... ]
         # you can know connect? by ret.name
         ret = self._run_api('connect', 'sth::connect', **kwargs)

         # create a special key to save your result
         ret.port_handles =  [ ]
         for port in re.split("\s+", kwargs['port_list']):
            port_handle = self.eval( 'keylget %s port_handle.%s.%s' % (ret.name, kwargs['device'], port))
            ret.port_handles.append(port_handle)
         
         logger.debug('sth_connect return: %s' % ret)
         return ret
   ```
2. **add more sth:: functions**<br/>
	you can modify the API.TXT file under package, add the sth:: function name to it<br/>