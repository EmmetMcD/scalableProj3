Requires python3.8 and asyncio.



Each device-name is in the constants file - update this for each new device in the network

genDrone is a handy tmux-based script that spins up all the Drone's sensors/actuators:

    source genDrone
    tmux attach

You can then use ctrl+B [INT] to look at different devices' loggings

For manual running:
Run the server:

    PYTHONPATH=. python3 ./drone/server.py
    
Run each sensor/actuator:

    PYTHONPATH=. python3 ./drone/[SENSOR].py

The sensors & their tags are as follows:
* ballast.py - subscribes to **depth** & **power**
* barometer.py - produces **depth** & **pressure**
* camera.py - produces **camera** (a 'boolean' that reports if "something worth doing science to is in camera view")
* compass.py - produces **angle**
* motor.py - subscribes to **xpos** & **ypos**
* positioning.py - produces **xpos** & **ypos**
* power.py - produces **power**
* sampler.py - subscribes to **camera**, **depth**, **xpos**, **ypos** and GLOBAL **scienceList** , produces GLOBAL **scienceList** (scienceList is a global list shared across the network that lists all coordinates where science was done)
* keychanger.py [EXPERIMENTAL] - THIS FILE IS NOT ACTIVATED BY genDrone! - attempts to broadcast an updated key that all other sensors would subscribe to, but encoding issues mean it does not work.
