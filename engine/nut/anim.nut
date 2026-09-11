// Copyright (C) Natuworkguy
// See the LICENSE file for GPLv3

function frame_starts(delays, count) {
    local starts = []
    local total = 0.0

    for (local i = 0; i < count; i += 1) {
        local delay = delays[i]

        if (delay < 0.0) {
            delay = 0.0
        }

        starts.append(total)
        total = total + delay
    }

    starts.append(total)

    return starts
}
