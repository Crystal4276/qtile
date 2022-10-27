import os
import subprocess

from libqtile import bar, layout, hook, qtile
from libqtile.log_utils import logger
from libqtile.config import Click, Drag, Group, Key, KeyChord, Match, Screen, Rule, DropDown
from libqtile.lazy import lazy
from libqtile.widget import Spacer

from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration, PowerLineDecoration

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

# Theme name : Catppuccin Mocha 
# https://github.com/catppuccin/catppuccin#-palettes
def init_colors():
    return [["#cdd6f4", "#cdd6f4"], # color 0 Blue Catppuccin Mocha
            ["#1e1e2e", "#1e1e2e"], # color 1 Base Catppuccin Mocha
            ["#9399b2", "#9399b2"], # color 2 Overlay 2 Catppuccin Mocha
            ["#f5c2e7", "#f5c2e7"], # color 3 Pink Catppuccin Mocha
            ["00000000", "00000000"], # color 4 Transparent
            ["#f3f4f5", "#f3f4f5"], # color 5 White
            ["#45475a", "#45475a"], # color 6 Surface0 Catppuccin Mocha
            ["#1e1e2ea9", "#1e1e2ea9"], # color 7 Base Catppuccin Mocha 66% transparency
            ["#f3f4f500", "#f3f4f500"], # color 8 White 66 % Tranparency
            ["#11111b", "#11111b"]] # color 9 Crust
colors = init_colors()

@lazy.function
def minimize_all(qtile):
    for win in qtile.current_group.windows:
        if hasattr(win, "toggle_minimize"):
            win.toggle_minimize()

mod = "mod4"

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    #Key([mod], "Left", lazy.layout.left(), desc="Move focus to left"),
    #Key([mod], "Right", lazy.layout.right(), desc="Move focus to right"),
    #Key([mod], "Down", lazy.layout.down(), desc="Move focus down"),
    #Key([mod], "Up", lazy.layout.up(), desc="Move focus up"),
    #Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    
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

#Toggle minimization/fullscreen/kill of windows
    Key([mod],"c", minimize_all(), desc="Toggle minimization of all window"),
    Key([mod],"f", lazy.window.toggle_fullscreen(), desc="Make window fullscreen"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

 # Launch Applications
    Key([mod],"e", lazy.spawn("nemo"), desc="Launch Nemo"),
    Key([mod],"w", lazy.spawn("/home/crystal/.config/qtile/rofi/bin/launcher"), desc="Launch Rofi"),
    Key([mod],"x", lazy.spawn("geany"), desc="Launch Geany editor"),
    Key([mod],"a", lazy.spawn("chromium"), desc="Launch Chromium browser"),
    Key([mod], "Return", lazy.spawn("gnome-terminal -e \"bash -c neofetch\";bash"), desc="Launch Terminal"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([],"Print", lazy.spawn("gnome-screenshot --interactive"), desc="Launch Screenshot"),

 # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),

 # Qtile commands
    Key([mod, "mod1"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload Qtile config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
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
    keys.append(Key([mod], i.name, lazy.function(go_to_group(i.name))))
    keys.append(Key([mod, "control"], i.name, lazy.window.togroup(i.name, switch_group=True), lazy.function(go_to_group(i.name)), desc="Switch to & move focused window to group {}".format(i.name)))

# Decoration setting for group clock Rect.Decoraction
decor_clock = {
    "decorations": [
        RectDecoration(
            colour="#94e2d5",
            line_width= 0,
            radius=[15, 15, 15, 15],
            filled=True,
            padding_y=10,
            padding_x=0,
            group=True,
            extrawidth=5,
        ),
    ],
}
# Decoration setting for group cpu Rect.Decoraction
decor_cpu = {
    "decorations": [
        RectDecoration(
            use_widget_background=True,
            #colour="#fab387",
            line_width= 0,
            radius=[15, 0, 0, 15],
            filled=True,
            padding_y=10,
            padding_x=4,
            group=True,
            clip=False,
        ),
        PowerLineDecoration(path="forward_slash",size=10,shift=0,padding_y=9),
    ],
}

# Decoration setting for group gpu Rect.Decoraction
decor_gpu = {
    "decorations": [
            RectDecoration(
            use_widget_background=True,
            #colour="#f9e2af",
			line_width= 0,
            radius=[0, 0, 0, 0],
            filled=True,
            padding_y=10,
            padding_x=0,
            group=True,
            clip=False,
        ),
			PowerLineDecoration(path="forward_slash",size=10,shift=0,padding_y=9),
    ],
}
# Decoration setting for group mem Rect.Decoraction
decor_mem = {
    "decorations": [
        RectDecoration(
            #colour="#a6e3a1",
            use_widget_background=True,
            line_width= 0,
            radius=[0, 15, 15, 0],
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
            colour="#45475a",
            line_width= 0,
            radius=[15, 15, 15, 15],
            filled=True,
            padding_y=10,
            padding_x=0,
            group=False,
        )
    ],
}

# Decoration setting for no grouping side screen Rect.Decoraction
decor_side = {
    "decorations": [
        RectDecoration(
            colour="#45475a",
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
    padding=10,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Spacer(length=15),   
                widget.Image(
                       filename="~/.config/qtile/images/arch-catppuccin.png",
                       background = colors[4],
                       margin_y = 3, 
                       margin_x= 0,
                       mouse_callbacks={"Button1": lazy.spawn("/home/crystal/.config/qtile/rofi/bin/launcher")},
                       #**decor_nogroup
                ),  
                widget.Spacer(length=5), 
                widget.CurrentLayoutIcon(scale = 0.66, use_mask = True, foreground=colors[3]), 
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
                widget.Spacer(length=8),   
                widget.GroupBox(
                       font="monospace",
                       fontsize = 35,
                       spacing = 10,
                       margin_y = 3,
                       margin_x = 15,
                       padding = 5,
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
                       theme_path="/usr/share/icons/Papirus-dark",
                       theme_mode="preferred",
                ),
                widget.Spacer(),
                widget.WindowName(fontsize=24, empty_group_string="",foreground=colors[0]),
                widget.Spacer(),
                widget.CheckUpdates(
                       font = "FontAwesome",
                       fontsize = 35,
                       custom_command = "checkupdates",
                       update_interval = 86400,
                       display_format = "  {updates}",
                       mouse_callbacks ={"Button1": lazy.spawn("gnome-terminal -e \"bash -c paru\";bash")},
                       no_update_string='',
                       colour_have_updates = colors[3], **decor_nogroup
                ),
                widget.Spacer(length=10),
                widget.Systray(
                       background=colors[4],
                       icon_size = 40,
                       padding = 10,
                ),
                widget.Spacer(length=10),
                widget.CPU(format=":{load_percent:2.0f}%", fontsize=24, foreground=colors[9],background="#fab387",update_interval=5, **decor_cpu),
                widget.NvidiaSensors(format=':{temp}°C', fontsize=24, foreground=colors[9], background='#f9e2af',update_interval=5, **decor_gpu),
                widget.Memory(format="﬙:{MemUsed:2.0f}{mm}", measure_mem='G', fontsize=24, foreground=colors[9], background='#a6e3a1', update_interval=5, **decor_mem),
                widget.Spacer(length=10),   
                widget.Clock( 
                       padding = 10,
                       foreground = colors[9],
                       fontsize = 24,
                       format="%A %d, %H:%M",
                       **decor_clock, 
                ),
                widget.ScriptExit(
                       exit_script='poweroff',
                       font = "FontAwesome", 
                       default_text="", 
                       fontsize=29, 
                       foreground="#181825", 
                       padding=0,
                       countdown_format= "{} ",
                       **decor_clock, 
                ),
                widget.Spacer(length=5,**decor_clock), 
                widget.Spacer(length=3) 
           ],
        60, background=colors[4], margin = [3,3,0,3], opacity=1,
        border_width=[0, 0, 0, 0],  # Draw top and bottom borders
        border_color=["#45475a", "#45475a", "#45475a", "#45475a"]  # Borders are magenta
        ), 
                       wallpaper="~/.config/qtile/images/wallhaven-dpqjwj-3440.png",
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
                       theme_path="/usr/share/icons/Papirus-dark",
                       theme_mode="preferred",
                ),
                widget.Spacer(), 
                widget.CPU(format=":{load_percent:2.0f}%", fontsize=22, foreground=colors[9],background="#fab387",update_interval=5, **decor_cpu),
                widget.NvidiaSensors(format=':{temp}°C', fontsize=22, foreground=colors[9], background='#f9e2af',update_interval=5, **decor_gpu),
                widget.Memory(format="﬙:{MemUsed:2.0f}{mm}", measure_mem='G', fontsize=22, foreground=colors[9], background='#a6e3a1', update_interval=5, **decor_mem),
                widget.Spacer(length=10),   
                widget.Clock( 
                       padding = 10,
                       foreground = colors[9],
                       fontsize = 22,
                       format="%H:%M",
                       **decor_clock, 
                ),
                widget.ScriptExit(
                       exit_script='poweroff',
                       font = "FontAwesome", 
                       default_text="", 
                       fontsize=26, 
                       foreground="#181825", 
                       padding=5,
                       countdown_format= "{} ",
                       **decor_clock, 
                ),
				widget.Spacer(length=5,**decor_clock), 
                widget.Spacer(length=3,), 
           ],
        55, background=colors[4], margin = [0,3,0,10],
        border_width=[0, 0, 0, 0],  # Draw top and bottom borders
        border_color=["#45475a", "#45475a", "#45475a", "#45475a"]  # Borders are magenta
        ),                       
					   wallpaper="~/.config/qtile/images/wallhaven-dpqjwj-3440.png",
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
                       theme_path="/usr/share/icons/Papirus-dark",
                       theme_mode="preferred",
                ),
                widget.Spacer(), 
                widget.CPU(format=":{load_percent:2.0f}%", fontsize=22, foreground=colors[9],background="#fab387",update_interval=5, **decor_cpu),
                widget.NvidiaSensors(format=':{temp}°C', fontsize=22, foreground=colors[9], background='#f9e2af',update_interval=5, **decor_gpu),
                widget.Memory(format="﬙:{MemUsed:2.0f}{mm}", measure_mem='G', fontsize=22, foreground=colors[9], background='#a6e3a1', update_interval=5, **decor_mem),
                widget.Spacer(length=10),
                widget.Clock( 
                       padding = 10,
                       foreground = colors[9],
                       fontsize = 22,
                       format="%H:%M",
                       **decor_clock, 
                ),
                widget.ScriptExit(
                       exit_script='poweroff',
                       font = "FontAwesome", 
                       default_text="", 
                       fontsize=26, 
                       foreground="#181825", 
                       padding=5,
                       countdown_format= "{} ",
                       **decor_clock, 
                ),
				widget.Spacer(length=5,**decor_clock), 
                widget.Spacer(length=3,), 
           ],
        55, background=colors[4], margin = [0,3,0,10],
        border_width=[0, 0, 0, 0],  # Draw top and bottom borders
        border_color=["#45475a", "#45475a", "#45475a", "#45475a"]  # Borders are magenta
        ),
                       wallpaper="~/.config/qtile/images/wallhaven-dpqjwj-3440.png",
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
    Click([mod], "Button2", lazy.window.bring_to_front()),
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
        Match(wm_class="blueberry.py"),  # blueberry-tray
        Match(wm_class="conky"),  # conky
        Match(wm_class="cinnamon-settings screensaver"),  # screensaver
        Match(wm_class="pavucontrol"),  # Pulseaudio mixer and sound sources
        Match(wm_class="virt-manager"), # Virtual Manager
                Match(title="branchdialog"),  # gitk
        Match(title="Calculator"), #calculator
        Match(title="pinentry"),  # GPG key password entry
      #  Match(title="Steam - News"),  # Steam news pop-up windows
        Match(wm_class="nm-connection-editor") # network-manager connection editor
    ], fullscreen_border_width = 0, border_width = 2, border_focus=colors[2], border_normal=colors[6]
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

# Activate group 6, 7, and 1 after startup
@hook.subscribe.startup_complete
def assign_groups_to_screens():
	if len(qtile.screens) != 1:
		try:
			qtile.groups_map["1"].toscreen(0)
			qtile.groups_map["6"].toscreen(1)
			qtile.groups_map["8"].toscreen(2)
		except IndexError:
			pass
