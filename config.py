import os
import subprocess
import asyncio
import psutil

from libqtile import bar, layout, hook, qtile
from libqtile.log_utils import logger
from libqtile.config import Click, Drag, Group, Key, KeyChord, Match, Screen, Rule, DropDown
from libqtile.lazy import lazy
from libqtile.widget import Spacer

from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration, PowerLineDecoration
from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupImage,
    PopupText
)

def show_power_menu(qtile):
    controls = [
        PopupImage(
            filename="~/.config/qtile/assets/lock.svg",
            pos_x=0,
            pos_y=0.02,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/lock_blur.svg",
            mouse_callbacks={"Button1": lazy.spawn('betterlockscreen -l dim -- --time-str="%H:%M"')}
        ),
        PopupText(
            text="Lock",
            font='monospace Bold',
            fontsize=18,
            pos_x=0,
            pos_y=0.17,
            width=1,
            height=0.075,
            foreground=colors[15],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.spawn('betterlockscreen -l dim -- --time-str="%H:%M"')}
        ),
        PopupImage(
            filename="~/.config/qtile/assets/logout.svg",
            pos_x=0.0,
            pos_y=0.27,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/logout_blur.svg",
            mouse_callbacks={"Button1": lazy.shutdown()}
        ),
        PopupText(
            text="Logout",
            font='monospace Bold',
            fontsize=18,
            pos_x=0.0,
            pos_y=0.42,
            width=1.0,
            height=0.075,
            foreground=colors[10],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.shutdown()}
        ),
        PopupImage(
            filename="~/.config/qtile/assets/restart.svg",
            pos_x=0.0,
            pos_y=0.52,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/restart_blur.svg",
            mouse_callbacks={"Button1": lazy.spawn("systemctl reboot")}
        ),
        PopupText(
            text="Restart",
            font='monospace Bold',
            fontsize=18,
            pos_x=0,
            pos_y=0.67,
            width=1,
            height=0.075,
            foreground=colors[12],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.spawn("systemctl reboot")}
        ),
        PopupImage(
            filename="~/.config/qtile/assets/shutdown.svg",
            pos_x=0,
            pos_y=0.77,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/shutdown_blur.svg",
            mouse_callbacks={"Button1": lazy.spawn("systemctl poweroff")}
        ),
        PopupText(
            text="Shutdown",
            font='monospace Bold',
            fontsize=18,
            pos_x=0,
            pos_y=0.92,
            width=1,
            height=0.075,
            foreground=colors[13],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.spawn("systemctl poweroff")}
        ),
    ]

    layout = PopupRelativeLayout(
        qtile,
        width=100,
        height=350,
        border_width=1,
        border=colors[6],
        controls=controls,
        background=colors[1],
        initial_focus=None,
        hide_interval=0.7,
        hide_on_mouse_leave=True
    )
    layout.show(x=-6, y=0.003, warp_pointer=False,relative_to=3,relative_to_bar=True)

# Parsing : remove all text.
def txt_remove(text):
    return ""

# Send a window within a group to group displayed on left or right screen. Three monitors configuration, monitor 0 is the central monitor -> Screens: [1,0,2] 
def window_to_previous_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i == 0:
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.to_screen(i + 1)
    if i == 2:
        group = qtile.screens[i - 2].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.to_screen(i - 2)

def window_to_next_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i == 0:
        group = qtile.screens[i + 2].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.to_screen(i + 2)
    if i == 1:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.to_screen(i - 1)

# Key bindings for group stick to screen
def go_to_group(name: str) -> callable:
    def _inner(qtile) -> None:
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return
        if name in "123":
            qtile.focus_screen(0)
            qtile.groups_map[name].toscreen()
        elif name in "456":
            qtile.focus_screen(1)
            qtile.groups_map[name].toscreen()
        else:
            qtile.focus_screen(2)
            qtile.groups_map[name].toscreen()
    return _inner

def _scroll_screen(direction: int) -> callable:
    """
    Scroll to the next/prev group of the subset allocated to a specific screen. This
    will rotate between e.g. 1->2->3->1 when the first screen is focussed.
    """
    def _inner(qtile: qtile):
        if len(qtile.screens) == 1:
            current = qtile.groups.index(qtile.current_group)
            destination = (current + direction) % 9
            qtile.groups[destination].toscreen()
            return
        current = qtile.groups.index(qtile.current_group)
        if current < 3:
            destination = (current + direction) % 3
        elif current < 6:
            destination = ((current - 3 + direction) % 3) + 3
        else:
            destination = ((current - 6 + direction) % 3) + 6
        qtile.groups[destination].toscreen()
    return _inner

# Theme name : Catppuccin Mocha 
# https://github.com/catppuccin/catppuccin#-palettes
def init_colors():
    return [["#cdd6f4", "#cdd6f4"], # color 0 Text (Blue) 
            ["#1e1e2e", "#1e1e2e"], # color 1 Base 
            ["#9399b2", "#9399b2"], # color 2 Overlay 2 
            ["#f5c2e7", "#f5c2e7"], # color 3 Pink 
            ["00000000", "00000000"], # color 4 Transparent
            ["#f3f4f5", "#f3f4f5"], # color 5 White
            ["#45475a", "#45475a"], # color 6 Surface 0
            ["#1e1e2ea9", "#1e1e2ea9"], # color 7 Base with 66% transparency
            ["#f3f4f500", "#f3f4f500"], # color 8 White 66 % tranparency for highlight
            ["#11111b", "#11111b"], # color 9 Crust
            ["#fab387", "#fab387"], # color 10 Peach
            ["#f9e2af", "#f9e2af"], # color 11 Yellow
            ["#a6e3a1", "#a6e3a1"], # color 12 Green
            ["#94e2d5", "#94e2d5"], # color 13 Teal (Blue/Green)
            ["#eba0ac", "#eba0ac"], # color 14 Maroon (Reddish/pink)
            ["#f38ba8", "#f38ba8"], # color 15 Red
            ["#89dceb", "#89dceb"], # color 16 Sky (Blue)
           ] 
colors = init_colors()

@lazy.function
def minimize_all(qtile):
    for win in qtile.current_group.windows:
        if hasattr(win, "toggle_minimize"):
            win.toggle_minimize()


mod = "mod4"

keys = [
    # Switch between windows
    Key([mod,"mod1"], "Left", lazy.layout.left(), desc="Move focus to left"),
    Key([mod,"mod1"], "Right", lazy.layout.right(), desc="Move focus to right"),
    Key([mod,"mod1"], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([mod,"mod1"], "Up", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    
    # Move windows between left/right columns or move up/down in current stack.
    Key([mod, "control"], "Left", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "control"], "Right", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "control"], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "control"], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
    
    # Grow windows.
    Key([mod, "shift"], "Left", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "shift"], "Right", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "shift"], "Down", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "shift"], "Up", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    #Key([mod], "d", lazy.function(go_to_group("8")), lazy.screen.toggle_group(group_name="8", warp=True)),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    #Key(
    #    [mod, "shift"],
    #    "Return",
    #    lazy.layout.toggle_split(),
    #    desc="Toggle between split and unsplit sides of stack",
    #),
    
    # Move window to next screen
    Key([mod], "Right", lazy.function(window_to_next_screen, switch_screen=True),desc="Move window to right screen"),
    Key([mod], "Left", lazy.function(window_to_previous_screen, switch_screen=True), desc="Move window to left screen"),

	# Toggle minimization/fullscreen/kill of windows
    Key([mod],"c", minimize_all(), desc="Toggle minimization of all window"),
    Key([mod],"f", lazy.window.toggle_fullscreen(), desc="Make window fullscreen"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

    # Toggle between different group and layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "quoteleft", lazy.function(_scroll_screen(1)), desc="Screen groups forward"),

	# Launch Applications
    Key([mod],"e", lazy.spawn("nemo"), desc="Launch Nemo"),
    Key([mod],"w", lazy.spawn(os.path.expanduser('~/.config/qtile/rofi/bin/launcher')), desc="Launch Rofi"),
    Key([mod],"x", lazy.spawn("geany"), desc="Launch Geany editor"),
    Key([mod],"a", lazy.spawn("chromium"), desc="Launch Chromium browser"),
    Key([mod],"s", lazy.function(show_power_menu), desc="Power Menu"),
    Key([mod], "Return", lazy.spawn("gnome-terminal -e \"bash -c neofetch\";bash"), desc="Launch Terminal"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([],"Print", lazy.spawn("gnome-screenshot --interactive"), desc="Launch Screenshot"),
    Key([mod], "u",lazy.spawn("nmcli con up Nederland-PPTP"), desc="Connect PureVPN"),
    Key([mod], "i",lazy.spawn("nmcli con down Nederland-PPTP"), desc="Disconnect PureVPN"),

	# Qtile commands
    Key([mod, "mod1"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload Qtile config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile and logout"),
]

groups = [
    Group("1", label=""),
    Group("2", label=""),
    Group("3", label=""), 
    Group("4", label="", matches=[Match(wm_class=["discord"])],layout = "max"),
    Group("5", label="", matches=[Match(wm_class=["spotify"])],layout = "max"),
    Group("6", label=""),
    Group("7", label="", matches=[Match(wm_class=["deluge"])],layout = "columns"),
    Group("8", label="", matches=[Match(wm_class=["evolution","thunderbird"])],layout = "max"),
    Group("9", label="", matches=[Match(wm_class=["Steam"])],layout = "max"),
]

for i in groups:
    keys.append(Key([mod], i.name, lazy.function(go_to_group(i.name)), desc="Switch to group {}".format(i.name)))
    keys.append(Key([mod, "control"], i.name, lazy.window.togroup(i.name, switch_group=True), lazy.function(go_to_group(i.name)), desc="Switch to & move focused window to group {}".format(i.name)))

# Decoration setting for group clock Rect.Decoraction
decor_clock = {
    "decorations": [
        RectDecoration(
            #colour="#94e2d5",
            use_widget_background=True,
            line_width= 0,
            radius=[15, 15, 15, 15],
            filled=True,
            padding_y=10,
            padding_x=0,
            group=True,
            extrawidth=0,
        ),
    ],
}

# Decoration setting for group mem Rect.Decoraction
decor_mem = {
    "decorations": [
        RectDecoration(
            #colour="#a6e3a1",
            use_widget_background=True,
            line_width= 0,
            radius=[15, 15, 15, 15],
            filled=True,
            margin_y=20,
            padding_y=10,
            padding_x=0,
            group=True,
            clip=False,
        )
    ],
}

# Decoration setting for no grouping Rect.Decoraction
decor_nogroup = {
    "decorations": [
        RectDecoration(
            colour=colors[1],
            #use_widget_background=True,
            line_width= 0,
            radius=[15, 15, 15, 15],
            filled=True,
            padding_y=10,
            padding_x=0,
            group=False,
        )
    ],
}

# Decoration setting for update Rect.Decoraction
decor_update = {
    "decorations": [
        RectDecoration(
            #colour="#f5c2e7",
            use_widget_background=True,
            line_width= 0,
            radius=[15, 15, 15, 15],
            filled=True,
            padding_y=10,
            padding_x=0,
            group=False,
        )
    ],
}

# Decoration setting for no grouping Rect.Decoraction
decor_exit = {
    "decorations": [
        RectDecoration(
            #colour="#45475a",
            use_widget_background=True,
            line_width= 0,
            radius=15,
            filled=True,
            padding_y=10,
            padding_x=0,
            group=True,
            clip=True,
            #extrawidth=-10,
        )
    ],
}
# Decoration setting for no grouping side screen Rect.Decoraction
decor_side = {
    "decorations": [
        RectDecoration(
            colour=colors[1],
            line_width=0,
            radius=[15, 15, 15, 15],
            filled=True,
            padding_y=7,
            padding_x=0,
            group=False,
        )
    ],
}

widget_defaults = dict(
    font="monospace",
    fontsize=30,
    padding=8,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Spacer(length=15),   
                widget.Image(
                       filename="~/.config/qtile/assets/arch_linux_icon_blue_pink.svg",
                       background = colors[4],
                       margin_y = 6, 
                       mouse_callbacks={"Button1": lazy.spawn(os.path.expanduser('~/.config/qtile/rofi/bin/launcher_icon'))},
                       #**decor_nogroup
                ),  
                widget.Spacer(length=5), 
                widget.CurrentLayoutIcon(
                       scale = 0.66, 
                       use_mask = True, 
                       foreground=colors[3],
                       ), 
           #     widget.LaunchBar(progs=[
           #             ('org.gnome.Terminal', 'gnome-terminal + "neofetch"', 'Launch terminal'),
           #             ('nemo', 'nemo', 'Launch File Manager'),
           #             ('chromium', 'chromium', 'Launch Chromium'),
                        #('discord', 'discord', 'Launch Discord'),
                        #('spotify', 'spotify', 'Launch Spotify'),
                        #('deluge', 'deluge', 'Launch deluge'),
                        #('thunderbird', 'thunderbird', 'Launch thunderbird'),
                        #('steam', 'steam', 'Launch Steam'),
           #                           ], 
           #             padding = 15, padding_y = -2, icon_size=40,**decor_nogroup
           #     ),
                #widget.Spacer(length=8),   
                widget.GroupBox(
                       font="monospace",
                       fontsize = 35,
                       spacing = 10,
                       margin_y = 3,
                       margin_x = 15,
                       padding = 5,
                       #background="#45475a",
                       disable_drag = True,
                       active = colors[3],
                       inactive = colors[2],
                       highlight_method='border',
                       this_current_screen_border = colors[3],
                       other_current_screen_border=colors[6],
                       this_screen_border=colors[3],
                       urgent_border=colors[3],
                       urgent_text=colors[3],
                       borderwidth = 3,
                       visible_groups=['1', '2', '3'],
                       **decor_nogroup
                ),
                widget.Spacer(length=5),
                widget.Prompt(),
                widget.Chord(
                      chords_colors={
                      "launch": ("#ff0000", "#ffffff"),
                       },
                       name_transform=lambda name: name.upper(),
                ),  
                widget.Spacer(length=5),
                widget.TaskList(
                       highlight_method="block",
                       border=colors[4],
                       borderwidth=0,
                       background = colors[4],
                       icon_size = 40,
                       padding_x = 1,
                       padding_y = 9,
                       margin_x= 5,
                       margin_y= 4,
                       spacing = 5,
                       parse_text=txt_remove,
                       fontsize = 20,
                       txt_floating="🗗",
                       txt_maximized="🗖",
                       txt_minimized="🗕",
                       theme_path="/usr/share/icons/Papirus-Dark",
                       theme_mode="preferred",
                ),
                widget.Spacer(),
                widget.WindowName(fontsize=24, empty_group_string="",foreground=colors[0]),
                widget.Spacer(),
                widget.CheckUpdates(
                       font = "FontAwesome",
                       fontsize = 30,
                       custom_command = "checkupdates",
                       update_interval = 86400,
                       display_format = "  {updates}",
                       mouse_callbacks ={"Button1": lazy.spawn("gnome-terminal -e \"bash -c paru\";bash")},
                       no_update_string='',
                       colour_have_updates = colors[3],
                       #background = colors[1],
                       #**decor_update
                ),
                widget.NvidiaSensors(
                    format=':{temp}°C', 
                    fontsize=24, 
                    foreground=colors[13], 
                    background=colors[1],
                    update_interval=5, 
                    mouse_callbacks ={"Button1": lazy.spawn("gnome-terminal -e \"bash -c watch -n2 nvidia-smi\"")}, 
                    **decor_mem
                    ),
                widget.CPU(
                    format=":{load_percent:2.0f}%", 
                    fontsize=24, 
                    foreground=colors[12],
                    background=colors[1],
                    update_interval=5,
                    mouse_callbacks ={"Button1": lazy.spawn("gnome-terminal -e \"bash -c btop\"")},  
                    **decor_mem),
                widget.Memory(
                    format="﬙:{MemUsed:2.0f}{mm}", 
                    measure_mem='G', 
                    fontsize=24, 
                    foreground=colors[11], 
                    background=colors[1], 
                    update_interval=5,
                    mouse_callbacks ={"Button1": lazy.spawn("gnome-terminal -e \"bash -c btop\"")},  
                    **decor_mem),
                widget.Spacer(length=10),
                widget.Clock( 
                       padding = 10,
                       foreground = colors[10],
                       background=colors[1],
                       fontsize = 24,
                       format=" %H:%M",
                       **decor_clock, 
                ),
                widget.Clock( 
                       padding = 10,
                       foreground = colors[14],
                       background=colors[1],
                       fontsize = 24,
                       format=" %a-%d",
                       **decor_clock,
                ),
                widget.Spacer(length=10),
                widget.ALSAWidget(
                       mouse_callbacks={"Button3": lazy.spawn("pavucontrol")},
                       mode='both',
                       theme_path="/usr/share/icons/Papirus-Dark",
                       icon_size=34,
                       fontsize=20,
                       padding=5,
                       bar_width=60,
                       bar_colour_high=colors[10],
                       bar_colour_loud=colors[15],
                       bar_colour_normal=colors[13],
                       bar_colour_mute=colors[1],
                       foreground=colors[5],
                       background=colors[1],
                       update_interval=5,
                       hide_interval=2,
                       **decor_exit,
                       ),
                widget.StatusNotifier(
                       icon_size=34,
                       icon_theme="/usr/share/icons/Papirus-Dark",
                       padding = 5,
                       hide_after=5,
                       menu_width=370,
                       show_menu_icons=True,
                       background=colors[1],
                       highlight_colour=colors[3],
                       menu_background=colors[1],
                       menu_foreground=colors[0],
                       menu_foreground_disabled=colors[2],
                       menu_icon_size=16,
                       menu_fontsize=16,
                       menu_foreground_highlighted=colors[9],
                       highlight_radius=7.5,
                       separator_colour=colors[15],
                       menu_border=colors[6],
                       menu_border_width=1,
                       menu_offset_x=2,
                       menu_offset_y=6,
                       **decor_exit,
				),
                widget.TextBox(
                       text="", 
                       fontsize=22, 
                       foreground=colors[15],
                       background=colors[1],
                       padding=-7,
                       **decor_exit,
				),   
                widget.TextBox(
                       mouse_callbacks={"Button1": lazy.function(show_power_menu), "Button3": lazy.function(show_power_menu)},
                       font = "FontAwesome", 
                       text="", 
                       fontsize=27, 
                       foreground=colors[5],
                       background=colors[1],
                       padding=12,
                       **decor_exit,
                ),
             #   widget.Spacer(length=1), 
             #   widget.Systray(
             #          background=colors[4],
             #          icon_size = 40,
              #         padding = 10,
             #   ),
           ],
        60, background=colors[4], margin = [2,4,0,0], opacity=1,
        border_width=[0, 0, 0, 0],  # Draw top and bottom borders
        border_color=["#45475a", "#45475a", "#45475a", "#45475a"]  # Borders are magenta
        ), 
                       wallpaper="~/.config/qtile/assets/wallhaven-dpqjwj-3440.png",
                       wallpaper_mode="fill",
	),

    Screen(
        top=bar.Bar(
            [
                widget.Spacer(-8), 
                widget.CurrentLayoutIcon(scale = 0.66, use_mask = True, foreground=colors[3]), 
                widget.GroupBox(
                       font="monospace",
                       fontsize = 35,
                       margin_x = 10,
                       spacing = 0,
                       margin_y = 2,
                       padding = 5,
                       disable_drag = True,
                       active = colors[3],
                       inactive = colors[2],
                       this_current_screen_border = colors[3],
                       this_screen_border=colors[3],
                       highlight_method='border',
                       borderwidth = 3,
                       visible_groups=['4', '5', '6'],
                       **decor_side
                ),
                widget.TaskList(
                       highlight_method="block",
                       border=colors[8],
                       borderwidth=0,
                       background = colors[4],
                       icon_size = 40,
                       fontsize= 25,
                       rounded = True,
                       padding_x = 1,
                       padding_y = 9,
                       margin_x= 5,
                       margin_y= 4,
                       spacing = 5,
                       parse_text=txt_remove,
                       txt_floating="🗗",
                       txt_maximized="🗖",
                       txt_minimized="🗕",
                       theme_path="/usr/share/icons/Papirus-Dark",
                       theme_mode="preferred",
                ),
                widget.Spacer(), 
                widget.NvidiaSensors(format=':{temp}°C', fontsize=22, foreground=colors[13], background=colors[1],update_interval=5, **decor_mem),
                widget.CPU(format=":{load_percent:2.0f}%", fontsize=22, foreground=colors[12],background=colors[1],update_interval=5, **decor_mem),
                widget.Memory(format="﬙:{MemUsed:2.0f}{mm}", measure_mem='G', fontsize=24, foreground=colors[11], background=colors[1], update_interval=5, **decor_mem),
                widget.Spacer(length=10),
                widget.Clock( 
                       padding = 10,
                       foreground = colors[10],
                       background=colors[1],
                       fontsize = 22,
                       format=" %H:%M",
                       **decor_clock, 
                ),
                widget.Spacer(length=3), 
           ],
        55, background=colors[4], margin = [0,3,0,10],
        border_width=[0, 0, 0, 0],  # Draw top and bottom borders
        border_color=["#45475a", "#45475a", "#45475a", "#45475a"]  # Borders are magenta
        ),                       
                       wallpaper="~/.config/qtile/assets/wallhaven-dpqjwj-3440.png",
                       wallpaper_mode="fill",
        ),
        
    Screen(
        top=bar.Bar(
            [
                widget.Spacer(-8), 
                widget.CurrentLayoutIcon(scale = 0.66, use_mask = True, foreground=colors[3]), 
                widget.GroupBox(
                       font="monospace",
                       fontsize = 36,
                       margin_x = 10,
                       spacing = 0,
                       margin_y = 4,
                       padding = 6,
                       disable_drag = True,
                       active = colors[3],
                       inactive = colors[2],
                       this_current_screen_border = colors[3],
                       this_screen_border=colors[3],
                       highlight_method='border',
                       borderwidth = 3,
                       visible_groups=['7', '8', '9'],
                       **decor_side
                ),
                widget.TaskList(
                       highlight_method="block",
                       border=colors[8],
                       borderwidth=0,
                       background = colors[4],
                       icon_size = 40,
                       fontsize=25,
                       rounded = True,
                       padding_x = 1,
                       padding_y = 9,
                       margin_x= 5,
                       margin_y= 4,
                       spacing = 5,
                       parse_text=txt_remove,
                       txt_floating="🗗",
                       txt_maximized="🗖",
                       txt_minimized="🗕",
                       theme_path="/usr/share/icons/Papirus-Dark",
                       theme_mode="preferred",
                ),
                widget.Spacer(),
                widget.Net(
                       padding=0,
                       foreground = colors[16],
                       background=colors[1],
                       fontsize = 22,
                       prefix ='M',
                       interface='eno2',
                       use_bits=False,
                       format=" {up} {down}",
                       update_interval=5,
                       **decor_clock,
                       ),
                widget.NetGraph(
                       padding = 0,
                       graph_color = colors[16],
                       background = colors[1],
                       border_width=2,
                       interface='eno2',
                       bandwidth_type= "down",
                       frequency=1,
                       margin_x=15,
                       margin_y=12,
                       samples=40,
                       **decor_clock,
                       ),
                widget.Spacer(10), 
                widget.NvidiaSensors(format=':{temp}°C', fontsize=22, foreground=colors[13], background=colors[1],update_interval=5, **decor_mem),
                widget.CPU(format=":{load_percent:2.0f}%", fontsize=22, foreground=colors[12],background=colors[1],update_interval=5, **decor_mem),
                widget.Memory(format="﬙:{MemUsed:2.0f}{mm}", measure_mem='G', fontsize=22, foreground=colors[11], background=colors[1], update_interval=5, **decor_mem),
                widget.Spacer(length=10),
                widget.Clock( 
                       padding = 10,
                       foreground = colors[10],
                       background=colors[1],
                       fontsize = 22,
                       format=" %H:%M",
                       **decor_clock, 
                ),
                widget.Spacer(length=3,), 
           ],
        55, background=colors[4], margin = [0,3,0,10],
        border_width=[0, 0, 0, 0],  # Draw top and bottom borders
        border_color=["#45475a", "#45475a", "#45475a", "#45475a"]  # Borders are magenta
        ),
                       wallpaper="~/.config/qtile/assets/wallhaven-dpqjwj-3440.png",
                       wallpaper_mode="fill",
    ),   
]

# Layout configuration
layout_theme = {"border_width": 1,
                "margin": 4,
                "border_focus": colors[2],
                "border_normal": colors[6]
                }
layouts = [
    layout.Columns(**layout_theme),
    # layout.Matrix(**layout_theme),
    #layout.RatioTile(**layout_theme),
    layout.Max(**layout_theme),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.MonadTall(),
    # layout.MonadWide(**layout_theme),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    #Click([mod], "Button2", lazy.window.bring_to_front()),
    Click([mod], "Button2", lazy.window.toggle_floating()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False

floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(wm_class="gnome-disks"),  # gnome disk utility
        Match(wm_class="blueman-manager"),  # blueman-applet
        Match(wm_class="conky"),  # conky
        Match(wm_class="cinnamon-settings screensaver"),  # screensaver
        Match(wm_class="pavucontrol"),  # Pulseaudio mixer and sound sources
        Match(wm_class="virt-manager"), # Virtual Manager
        Match(title="branchdialog"),  # gitk
        Match(title="Calculator"), #calculator
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class="nm-connection-editor") # network-manager connection editor
		], 
    fullscreen_border_width = 0, border_width = 2, border_focus=colors[2], border_normal=colors[6]
)

auto_fullscreen = True
focus_on_window_activation = "smart" #or focus
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# Window Manager Name 
wmname = "Qtile"

# If Spotify opens move it to proper group
@hook.subscribe.client_name_updated
def spotify(window):
    if window.name == "Spotify":
        window.togroup(group_name="5")

# Keep floating window always above
@hook.subscribe.group_window_add
def window_added(group, window):
    if window.floating:
        window.bring_to_front()
    else:
        for win in reversed(group.focus_history):
            if win.floating:
                win.bring_to_front()
                return
# Autostart
@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.Popen([home])

# Pass every Steam window that is not the main one in floating mode
@hook.subscribe.client_new
def float_steam(window):
    wm_class = window.window.get_wm_class()
    w_name = window.window.get_name()
    if (
        wm_class == ("Steam", "Steam")
        and (
            w_name != "Steam"
            # w_name == "Friends List"
            # or w_name == "Screenshot Uploader"
            # or w_name.startswith("Steam - News")
            or "PMaxSize" in window.window.get_wm_normal_hints().get("flags", ())
        )
    ):
        window.floating = True
    elif w_name == "EVE":
        window.togroup("3")
        qtile.groups_map["3"].toscreen(0)
    elif w_name == "Wine System Tray":
        window.togroup("9")


# Activate group 6, 7, and 1 after startup
@hook.subscribe.startup_complete
def assign_groups_to_screens():
	if len(qtile.screens) != 1:
		try:
			qtile.groups_map["1"].toscreen(0)
			qtile.groups_map["6"].toscreen(1)
			qtile.groups_map["8"].toscreen(2, toggle=True)
		except IndexError:
			pass

# Activate VPN. nm-applet needs to be loaded before attempting to connect to VPN. This is the reason of asyncio.sleep()
@hook.subscribe.startup_complete
async def start_vpn():
	await asyncio.sleep(2)
	qtile.spawn("nmcli con up Nederland-PPTP")

# Swallow application launched from gnome terminal
@hook.subscribe.client_new
def _swallow(window):
    pid = window.window.get_net_wm_pid()
    ppid = psutil.Process(pid).ppid()
    cpids = {c.window.get_net_wm_pid(): wid for wid, c in window.qtile.windows_map.items()}
    for i in range(5):
        if not ppid:
            return
        if ppid in cpids:
            parent = window.qtile.windows_map.get(cpids[ppid])
            if parent.window.get_wm_class()[0] != "gnome-terminal-server":
                return
            parent.minimized = True
            window.parent = parent
            return
        ppid = psutil.Process(ppid).ppid()

@hook.subscribe.client_killed
def _unswallow(window):
    if hasattr(window, 'parent'):
        window.parent.minimized = False

# Send any applications opened on screen 2 to screen 0 and apply Max layout
@hook.subscribe.client_managed
async def _screen0(window):
    wm_class = window.window.get_wm_class()
    w_name = window.window.get_name()
    #logger.warning(wm_class)
    #logger.warning(w_name)
    if ((window.group.screen.index == 2) 
        and (wm_class != ['Mail', 'thunderbird']) 
        and (wm_class != ['deluge', 'Deluge-gtk'])
        and (wm_class != ['deluge', 'Deluge'])  
        and (wm_class != ['Steam', 'Steam'])
    ):
        window.togroup("3")
        qtile.groups_map["3"].toscreen(0)
        #window.group.setlayout("max")
    elif w_name == "Wine System Tray":
        window.togroup("9")
    elif w_name == "EVE Launcher":
        window.togroup("9")
        window.center
    elif w_name =="EXAPUNKS":
        window.togroup("3")
        window.toggle_floating()
        qtile.groups_map["3"].toscreen(0)
        #window.group.setlayout("max")
