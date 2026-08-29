// Copyright (C) Natuworkguy
// See the LICENSE file for GPLv3

function clamp(value, low, high) {
    if (value < low) {
        return low
    }

    if (value > high) {
        return high
    }

    return value
}
