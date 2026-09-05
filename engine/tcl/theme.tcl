# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

set font [dict create]

dict set font default [list "Segoe UI" 10]
dict set font small   [list "Segoe UI" 9]

set ui_color [dict create]

dict set ui_color selected_background #0078D7
dict set ui_color text                #333333
dict set ui_color selected_foreground #FFFFFF

if {[tk windowingsystem] eq "aqua"} {
    dict set ui_color tooltip_background systemWindowBackgroundColor
    dict set ui_color tooltip_foreground systemTextColor
} else {
    dict set ui_color tooltip_background #F0F0F0
    dict set ui_color tooltip_foreground [dict get $ui_color text]
}

option add *selectedBackground      [dict get $ui_color selected_background]
option add *selectedForeground      [dict get $ui_color selected_foreground]

option add *Font                    [dict get $font default]
option add *Button.Font             [dict get $font default]
option add *Label.Font              [dict get $font default]
option add *Entry.Font              [dict get $font default]
option add *LabelFrame.Font         [dict get $font small]

option add *LabelFrame.relief       solid

option add *Tooltip*background      [dict get $ui_color tooltip_background]
option add *Tooltip*foreground      [dict get $ui_color tooltip_foreground]
