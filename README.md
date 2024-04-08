# pi_control_hub

A universal remote control hub.

## Special configurations

### Disable Wifi power management

After a certain amount of time, Wifi enters power saving mode on the Raspberry Pi
and it only wakes up, if a request is made from the Raspberry Pi to the outside.
Connections from the outside to the Raspberry Pi aren't possible then. To make sure
that the Raspberry Pi is always available, power management shall be turned off by
adding the following line to the file `/etc/rc.local`

```bash
/sbin/iwconfig wlan0 power off
```

### Install pip

On Raspberry Pi OS (bookworm) isn't installed out of the box so it should be
installed:

```bash
sudo apt-get install --no-install-recommends --no-install-suggests pip
```
