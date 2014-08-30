Getting Started
===============

copy `rtconsole.py` into you project, and include on top of your main script:

    from rtconsole import start_console
    start_console(locals())

You can give it any dictionary instead of `locals()` if you prefer, however `globals()` may not work. 
