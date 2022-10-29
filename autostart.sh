#!/bin/sh

#Define missing resolution
#xrandr --newmode "3440x1440_100.00"  729.56  3440 3728 4112 4784  1440 1441 1444 1525  -HSync +Vsync 
#xrandr --addmode Virtual-1 3440x1440_100.00
#xrandr --output Virtual-1 --mode 3440x1440_100.00

#starting utility applications at boot time
nm-applet &
#pamac-tray &
#nitrogen --restore &
picom --config $HOME/.config/qtile/scripts/picom.conf --experimental-backends &
#alttab -w 1 -d 2 -i 120x80 -t 120x80 -bg "#1e1d2d" -fg "#d9e0ee" -frame "#f5c2e7" -bw 5 -inact "#1e1d2d" -bc "#000000" -bw 0 -theme hicolor &
blueberry-tray &
# /home/crystal/.conky/conky-startup.sh
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
#run variety &

#starting user applications at boot time
volumeicon &
thunderbird &
nohup deluge &
discord &
spotify &
steam &




