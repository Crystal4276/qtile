from libqtile.lazy import lazy

from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupImage,
    PopupText
)

# Theme name : Catppuccin Mocha 
# https://github.com/catppuccin/catppuccin#-palettes
def init_colors():
    return [["#cdd6f4", "#cdd6f4"], # color 0 Text (Blue) 
            ["#1e1e2e", "#1e1e2e"], # color 1 Base #1e1e2e
            ["#9399b2", "#9399b2"], # color 2 Overlay 2 
            ["#f5c2e7", "#f5c2e7"], # color 3 Pink 
            ["00000000", "00000000"], # color 4 Transparent
            ["#f3f4f5", "#f3f4f5"], # color 5 White
            ["#45475a", "#45475a"], # color 6 Surface 0
            ["11111bbf"], # color 7  Crust 75% transparency # Base 85% transparency 1e1e2ed9
            ["#f3f4f500", "#f3f4f500"], # color 8 White 66 % tranparency for highlight
            ["#11111b", "#11111b"], # color 9 Crust
            ["#fab387", "#fab387"], # color 10 Peach
            ["#f9e2af", "#f9e2af"], # color 11 Yellow
            ["#a6e3a1", "#a6e3a1"], # color 12 Green
            ["#94e2d5", "#94e2d5"], # color 13 Teal (Blue/Green)
            ["#eba0ac", "#eba0ac"], # color 14 Maroon (Reddish/pink)
            ["#f38ba8", "#f38ba8"], # color 15 Red
            ["#89dceb", "#89dceb"], # color 16 Sky (Blue)
            ["#585b70"], # color 17 Surface 2 (grey)
           ] 
colors = init_colors()

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
            text="Reboot",
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
        border=colors[17],
        controls=controls,
        background=colors[7],
        initial_focus=None,
        hide_interval=0.7,
        hide_on_mouse_leave=True
    )
    layout.show(x=-6, y=0.003, warp_pointer=False,relative_to=3,relative_to_bar=True)
