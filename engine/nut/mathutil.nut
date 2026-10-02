// Copyright (C) Natuworkguy
// See the LICENSE file for GPLv3

// value: float
// low: float
// high: float
function clamp(value, low, high) {
    if (value < low) {
        return low
    }

    if (value > high) {
        return high
    }

    return value
}
