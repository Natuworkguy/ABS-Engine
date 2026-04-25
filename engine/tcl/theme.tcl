set font [dict create]

dict set font default [list "Segoe UI" 10]
dict set font small   [list "Segoe UI" 9]

set ui_color [dict create]

dict set ui_color background          #FFFFFF
dict set ui_color selected_background #0078D7
dict set ui_color text                #333333
dict set ui_color selected_foreground #FFFFFF

option add *foreground              [dict get $ui_color text]
option add *background              [dict get $ui_color background]
option add *selectedBackground      [dict get $ui_color selected_background]
option add *selectedForeground      [dict get $ui_color selected_foreground]

option add *Font                    [dict get $font default]
option add *Button.Font             [dict get $font default]
option add *Label.Font              [dict get $font default]
option add *Entry.Font              [dict get $font default]
option add *LabelFrame.Font         [dict get $font small]
option add *LabelFrame.foreground   [dict get $ui_color text]
option add *LabelFrame.background   [dict get $ui_color background]

option add *LabelFrame.relief       solid


proc get_color {color_name} {
    global ui_color

    if {[dict exists $ui_color $color_name]} {
        return [dict get $ui_color $color_name]
    }

    error "get_color: Invalid color name: \"$color_name\""
}
