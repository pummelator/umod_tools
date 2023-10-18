## UMOD Tool
This is a simple command-line only Python script for viewing and extracting the contents of UMOD archive files. This should work with both .umod files (Unreal, Unreal Tournament 1999) and .ut2mod files (Unreal Tournament 2003, UT2004). There is no functionality for creating UMOD files and there is no plan for it to be added.

Other than an included Python library for reading UMOD files, this program only uses standard Python libraries. Only a Python 3 installation is needed to run UMOD Tools.

#### Usage
This is the general usage of umod_tool.py:
`python3 umod_tool.py [UMOD_PATH] [OPTION] [OUT_PATH]`

The UMOD PATH is the path to the .umod or .ut2mod file to view or extract from. OUT PATH is the path to the file or directory to output to. Most commands can also print information to the terminal if no OUT PATH is specified. OPTION tells the program what to do with the UMOD and can be any of the following:
- Showing the UMOD's metadata (**-meta**), file list (**-files**), or both (**-fmeta**)
- Listing or extracting the Manifest files (**-man**, **-mant**, **-man2**)
- Extracting the files to a directory (**-ex**)

If no OPTION is given, the program defaults to **-fmeta**. The **-ex** option extracts all files except for Manifest.ini and Manifest.int. Extracting these files into a game installation can replace the existing Manifest files and require a reinstall. An option to extract these files along with the rest has also been included. For more information about the commands, see doc/cmd_usage.txt

#### Credit
The information about the UMOD format used to make the program was found at [UnrealWiki](https://beyondunrealwiki.github.io), specifically [this](https://beyondunrealwiki.github.io/pages/umod-file-format.html) page about the format and [this](https://beyondunrealwiki.github.io/pages/package-file-format-data-de.html) page about the compact index values and how filenames are stored in the archive.
