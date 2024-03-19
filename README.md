# SysMessage

---

This project consists of three files.

1. **sysmessage.py** - This is the source code
2. **configs.cfg** - A configuration file in which all options can be defined. 
3. **sysmessage_light.py** A lightweight alternative without logging, for better readability
**daily.message.example.md** is just an example of how a logfile would look like,

---

- The **configs.cfg** file should be placed in the same directory as the Python script to ensure proper functionality. 
- It is important to note that the variable `number_of_commands` must correspond exactly to the number of commands to be executed, otherwise some commands will not be executed. 

---
- The script reads the Linux commands to be executed under `[commands-config]`, executes them sequentially and saves their output in the **daily-message.md** file.
- The file will then be read by the E-Mail handler, which is configured under `[email-config]` and sent via configured SMTP-Server.
- The option `versioning` enables the skript to save old logfiles to the folder */old-logs*, which will be auto-generated.
---



- The loglevel option can be used to control the level at which the logging of the script should be done.
  - Logging information is also added to the **daily-message.md** file. 
  - For available log-levels, refer to the [official docu](https://docs.python.org/3/library/logging.html#logging-levels).
- The variable `timeformat` defines the formatting of the timestamps for logging and in the header of **daily-message.md**. 
  - Available formatting can be seen [here](https://strftime.org/).
