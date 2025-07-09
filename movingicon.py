import msvcrt
import sys
import time

import commctrl as cc
import win32gui as wgui


def main(*argv):
    search_criteria = (
        (0, "Progman", None),
        (0, "SHELLDLL_DefView", None),
        (0, "SysListView32", None),
    )
    wnd = 0
    for crit in search_criteria:
        wnd = wgui.FindWindowEx(wnd, *crit)
        if wnd == 0:
            print("Could not find child matching criteria: {:}".format(crit))
            return
    idx = 0
    for i in range(0, 1000, 16):
        lparam = (i << 16) | i
        print("{:d} - 0x{:08X}".format(i, lparam))
        wgui.SendMessage(wnd, cc.LVM_SETITEMPOSITION, idx, lparam)
        time.sleep(0.5)
        if msvcrt.kbhit():
            break


if __name__ == "__main__":
    print("Python {:s} {:03d}bit on {:s}\n".format(" ".join(elem.strip() for elem in sys.version.split("\n")),
                                                   64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    rc = main(*sys.argv[1:])
    print("\nDone.")
    sys.exit(rc)