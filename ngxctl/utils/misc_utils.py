import os
import time


def display_report(processor, interval=1):
    if os.name == 'posix':
        import curses
        import atexit
        import signal

        scr = curses.initscr()
        atexit.register(curses.endwin)

        def print_report(sig, frame):
            output = processor.report()
            scr.erase()
            try:
                scr.addstr(output)
            except curses.error:
                pass
            scr.refresh()

        signal.signal(signal.SIGALRM, print_report)
        signal.setitimer(signal.ITIMER_REAL, 0.1, interval)
    else:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(processor.report())
            time.sleep(1)