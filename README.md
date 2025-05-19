* Known Issue: Image outputs can sometimes not be forced to 50 frames, see fix [here](https://github.com/chris-erb/Win-AEDAT-File-Reader).
# AEDAT File Reader

This is a Python variation of [Aedat File Reader Rs](https://github.com/Mibblez/aedat-file-reader-rs) for use with the DVS120 and DVS240.

Thank you, Anthony Beninati, for this code's base-framework in Rust.
<br />

---

### Author: 

Christopher Erb

cerb01@manhattan.edu
<br />

---

### Verison History: 

**v1.0** - 10/25/2024

*Notes: First implementation.*

<br />

**v1.1** - 11/08/2024

*Notes: - Added functionality for converting from png to raw images.*

<br />


---

## PyCharm Run Configurations

### CSV run config:

Script: C:/Users/ **name**/PycharmProjects/aedat_file_converter/run.py

Parameters: --csv --include-polarity --coords

Working Directory: C:\Users\ **name**\PycharmProjects\aedat_file_converter
<br />
<br />
<br />
<br />
### PNG run config:

Script: C:/Users/ **name**/PycharmProjects/aedat_file_converter/run.py

Parameters: --video --time_based --window-size 5000 --max-frames 50 --keep-frames --omit-video

Working Directory: C:\Users\ **name**\PycharmProjects\aedat_file_converter
<br />
<br />
<br />
<br />
### AVI (video) run config:

Script: C:/Users/ **name**/PycharmProjects/aedat_file_converter/run.py

Parameters: --video --time_based --window-size 5000 --max-frames 50

Working Directory: C:\Users\ **name**\PycharmProjects\aedat_file_converter

---
## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/chris-erb/Aedat_File_Reader/blob/main/LICENSE) file for details

