# changelist
* 1.0.1,  update brief
* 1.0.0,  support stc:: sth:: tclsh call

# feedback
* send email to dvdface@gmail.com
* visit https://github.com/dvdface/spirentapi

# how to install
`pip install spirentapi`

# known issues

Greate FireWall in China may prevent teacup install Tclx and ip pakcages<br/>

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
Sometimes, it's not convenience to access result of sth:: command by dot<br/>

for example:<br/>

```
conn_ret = api.sth_connect(device='10.182.32.138', port_list='1/1 1/11', break_locks=1)

# access port handle is very unconvenience
conn_ret['port_handle']['10']['182']['32']['138']['1/1']

# so you can extend SpirentAPI, add a sth_connect function to override dynamically created function
class MyExtendedAPI(SpirentAPI):

   def sth_connect(self, **kwargs):

      assert type(kwargs) == dict

      # use _run_api to run sth::connect
      # connect is the variable name, based on this name to create a variable to save sth::connect result
      ret = self._run_api('connect', 'sth::connect', **kwargs)

      # create a special key to save your result
      ret.port_handles =  [ ]
      for port in re.split("\s+", kwargs['port_list']):
         port_handle = self.eval( 'keylget %s port_handle.%s.%s' % (ret.name, kwargs['device'], port))
         ret.port_handles.append(port_handle)
        
      logging.getLogger().debug('sth_connect return: %s' % ret)
      return ret
```