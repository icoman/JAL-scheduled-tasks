#Schedule tasks in JAL with TMR0

JAL code generator written in [python 2.7](https://www.python.org/) and [PythonCard](http://pythoncard.sourceforge.net/) - [blog announcement](http://rainbowheart.ro/533).

Use this code to quick generate and compile a JAL application.

The application generate initialize JAL code for selected PIC processor, for TMR0 and for interrupt routine of TMR0. The interrupt routine of TMR0 advance counters and let tasks be executed when are scheduled.

In the next image, TMR0 is configured to generate interrupts each millisecond. 

![JAL Scheduled Tasks with TMR0](http://rainbowheart.ro/static/uploads/1/2017/3/jalscheduledtasks.jpg)

I have discovered that after 11 years since latest update (2006) of [PythonCard](http://pythoncard.sourceforge.net/), the solution still works in Windows, Linux and OpenBSD, even with latest [wx Python](https://wxpython.org/), 3.0.2.0.

I have many projects based on [PythonCard](http://pythoncard.sourceforge.net/) which works both on Windows and Linux.

License-free software.

Feel free to use this software for both personal and commercial usage.

Bonus: **cx_freeze** and **pyinstaller** scripts.
