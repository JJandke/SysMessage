# SysMessage

---

This project consists of two files.

1. **sysmessage.py** - This is the source code
2. **configs.cfg** - A configuration file in which all options can be defined. 

---

- The **configs.cfg** file should be in the same directory as the Python script to ensure proper functionality. 
- The script reads the Linux commands to be executed under `[commands-config]`, executes them sequentially and saves their output in the **daily-message.md** file. 
This is to be sent by e-mail, but is not yet implemented. 

- It is important to note that the variable `number_of_commands` must correspond exactly to the number of commands to be executed, otherwise some commands will not be executed. 

- The loglevel option can be used to control the level at which the logging of the script should be done.
Logging information is also added to the **daily-message.md** file. 
- The variable `timeformat` defines the formatting of the timestamps for logging and in the header of **daily-message.md**.  Available formatting can be seen [here](https://strftime.org/).
