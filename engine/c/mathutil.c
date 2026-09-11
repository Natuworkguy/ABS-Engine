// Copyright (C) Natuworkguy
// See the LICENSE file for GPLv3

#include "mathutil.h"

double clamp(double value, double low, double high) {
    if (value < low) {
        return low;
    }

    if (value > high) {
        return high;
    }

    return value;
}
