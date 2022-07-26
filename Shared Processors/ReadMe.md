Shared Processors
======

This readme will give a short description for each processor and which recipes the processor is used in.  This is for usage examples and my own sanity if I update one and don't remember where all I've used it.


## AutoDeskPatchProcessor ##

This processor finds the URL for the latest patch of the supplied major version of an AutoDesk product.  Should support all products and major versions.

Used in:
  * com.github.mlbz521.download.AutoCADPatch


## CanonPrintDriverProcessor ##

Downloads and packages the latest Canon driver package based on the override-able parameters:  model, OS Version, and download type.

Notables:
  * Processor was originally written to download the UFRII drivers, but has been updated to also download drivers for Canon's Multi-Function Printers as well
  * This Processor inherits from the SeleniumWebScrapper Processor
  * This processor technically can support Linux, macOS, _and_ Windows
  * See the requirements for the SeleniumWebScrapper Processor

Input Variables:
  * model:
    * description:  The official model name of the Canon Printer to search for
    * required:  True
    * example:  'imageRUNNER ADVANCE C7565i III'
  * download_type:
    * description:  What to download from the available list.  Options:
  	  * Recommended
        * Will download _whatever_ option is in the "Recommended Driver(s)" section
		      * _Note_:  the "Recommended" driver may not be the *_latest_* driver
      * UFRII
        * will download the latest UFRII optional driver
      * PS
        * will download the latest PS optional driver
      * FAX
        * will download the latest FAX optional driver
      * PPD
        * will download the latest PPD optional driver
        * Note:  The `com.github.mlbz521.pkg.CanonPrintDriver` recipe does not support the PPD file type
  * os_version
    * description:  The OS version to search against
    * required:  False
    * default:  'MACOS_12' (i.e. Monterey)
    * options:  
      * macOS Monterey v12.0:  MACOS_12
      * macOS Big Sur v11.0:  MACOS_11
      * macOS Catalina v10.15:  MACOS_10_15
      * macOS Mojave v10.14:  MACOS_10_14
      * macOS High Sierra v10.13:  MACOS_10_13
      * macOS Sierra v10.12:  MACOS_V10_12
      * OS X El Capitan v10.11:  OS_X_V10_11
      * OS X Yosemite v10.10:  OS_X_V10_10
      * OS X Mavericks v10.9:  OS_X_V10_9
      * OS X Mountain Lion v10.8:  MAC_OS_X_V10_8
      * OS X Lion v10.7:  MAC_OS_X_V10_7
      * Mac OS X Snow Leopard v10.6:  MAC_OS_X_V10_6
      * Mac OS X v10.1:  MAC_OS_X_V10_1
      * Mac OS 9:  MAC_OS_9
      * Windows 10 (x64):  WINDOWS_10_X64
      * Windows 10:  WINDOWS_10
      * Windows 8.1 (x64):  WINDOWS_8_1_X64
      * Windows 8.1:  WINDOWS_8_1
      * Windows 8 (x64):  WINDOWS_8_X64
      * Windows 8:  WINDOWS_8
      * Windows 7 (x64):  WINDOWS_7_X64
      * Windows 7:  WINDOWS_7
      * Windows Vista (x64):  WINDOWS_VISTA_X64
      * Windows Vista:  WINDOWS_VISTA
      * Windows XP (x64):  WINDOWS_XP_X64
      * Windows XP:  WINDOWS_XP
      * Windows Me:  WINDOWS_ME
      * Windows 98:  WINDOWS_98
      * Windows 95:  WINDOWS_95
      * Windows Server 2019 (x64):  WINDOWS_SERVER_2019_X64
      * Windows Server 2016 (x64):  WINDOWS_SERVER_2016_X64
      * Windows Server 2012 R2 (x64):  WINDOWS_SERVER_2012_R2_X64
      * Windows Server 2012 (x64):  WINDOWS_SERVER_2012_X64
      * Windows Server 2008 R2 (x64):  WINDOWS_SERVER_2008_R2_X64
      * Windows Server 2008 (x64):  WINDOWS_SERVER_2008_X64
      * Windows Server 2008:  WINDOWS_SERVER_2008
      * Windows Server 2003 R2 (x64):  WINDOWS_SERVER_2003_R2_X64
      * Windows Server 2003 R2:  WINDOWS_SERVER_2003_R2
      * Windows Server 2003 (x64):  WINDOWS_SERVER_2003_X64
      * Windows Server 2003:  WINDOWS_SERVER_2003
      * Linux 32bit:  LINUX_32BIT
      * Linux 64bit:  LINUX_64BIT
      * Linux ARM:  LINUX_ARM
      * Linux MIPS:  LINUX_MIPS
  * support_url
    * description:  The URL to the Canon product support page
    * required:  False
  * web_driver
    * description:  The web driver engine to use
    * required:  False
    * default:  Chrome
  * web_driver_path
    * description:  The OS version to search against
    * required:  False
    * default:  $PATH

Used in:
  * com.github.mlbz521.download.CanonPrintDriver


## CFBundleInfo ##

Supply a path to a plist file, which can point to a path inside a .dmg which will be mounted, and will returns four output_variables, which you can decide how to use:
  * CFBundleVersion
  * CFBundleShortVersionString
  * CFBundleIdentifier
  * version (CFBundleShortVersionString)

Used in:
  * com.github.mlbz521.pkg.RealVNCViewer
  * com.github.mlbz521.pkg.VOSviewer


## ConditionalUnarchiver ##

This process provides a condition wrapper around the Core Unarchiver Processor.

If extraction is needed, it uses Unarchiver to do and then (optionally) uses the FileFinder Processor to locate an extracted file.

If extraction is not needed, the processor simply assigns the %pathname% env variable to the value of the %found_filename% env variable.

Used in:
  * com.github.mlbz521.download.CanonPrintDriver


## ExtractWith7z ##

This processor extracts files with a specified 7zip binary.

Input Variables:
  * archive_path
    * description:  Path to an archive.  Defaults to contents of the 'pathname' variable, for example as is set by URLDownloader.
    * required:  False
  * destination_path
    * description:  Directory where archive will be unpacked, created if necessary. Defaults to RECIPE_CACHE_DIR/NAME.
    * required:  False
  * purge_destination
    * description:  Whether the contents of the destination directory will be removed before unpacking.
    * required:  False
  * 7z_path
    * description:  Path to a 7z-compatible binary.  This does not ship with macOS, it will need to be installed manually. The processor will prioritize a provided binary, but if it cannot locate it, it'll continue trying to find a 7z-compatible binary in common locations, including the system PATH.
    * required:  False

Used in:
  * com.github.mlbz521.download.MaplePatch
  * com.github.mlbz521.pkg.MatlabUpdate


## FileMode ##

This processor essentially runs `chmod` on a file.  Provide the numeric mode for file in octal format.

Used in:
  * com.github.mlbz521.pkg.Anaconda
  * com.github.mlbz521.pkg.SPSSStatisticsLegacy
  * com.github.mlbz521.pkg.SPSSStatisticsPatch


## FindFileInSearchPath ##

Borrowed and customized the find_file_in_search_path function from [JSSImporter.py](https://github.com/jssimporter/JSSImporter/blob/master/JSSImporter.py).  Searches search_paths for the first existing instance of path.  Searches, in order, through the following directories until a matching file is found:
  1. Path as specified.
  2. The parent folder of the path.
  3. First ParentRecipe's folder.
  4. First ParentRecipe's parent folder.
  5. Second ParentRecipe's folder.
  6. Second ParentRecipe's parent folder.
  7. Nth ParentRecipe's folder.
  8. Nth ParentRecipe's parent folder.

This search-path method is primarily in place to support using recipe overrides. It allows users to avoid having to copy templates, icons, etc, to the override directory.

**I added additional functionality to support storing files in a sub directory of the recipes parent directory.**

Used in:
  * com.github.mlbz521.pkg.JamfProTools
  * com.github.mlbz521.jss.PhETLabSimulations
  * com.github.mlbz521.pkg.PhETLabSimulations


## InputVariableTextSubstituter ##

This processor substitutes character(s) in a string with either another string or the value of a set autopkg variable and then returns the modified string as a supplied variable.

I wrote it to be able to substitute values into an input variable for when you want to use, for example the version in an input variable, but the version variable has not been set yet, not until the (child) recipe runs.  However, it can be used to substitute strings in any other strings.

Used in:
  * com.github.mlbz521.jss.ARCHICAD
  * com.github.mlbz521.jss.ARCHICADPatch
  * com.github.mlbz521.jss.AutoCAD
  * com.github.mlbz521.pkg.AutoCAD
  * com.github.mlbz521.jss.AutoCADPatch
  * com.github.mlbz521.jss.JMP
  * com.github.mlbz521.jss.JMPPro
  * com.github.mlbz521.jss.Maple
  * com.github.mlbz521.jss.Mathematica
  * com.github.mlbz521.jss.Matlab
  * com.github.mlbz521.jss.MatlabUpdate
  * com.github.mlbz521.jss.SPSSStatistics 
  * com.github.mlbz521.pkg.SPSSStatisticsLegacy
  * com.github.mlbz521.pkg.SPSSStatisticsPatch


## JVMVersioner ##

This processor finds the Java Virtual Machine version in a JDK package.  This will allow you to use which OpenJDK distribution you would like, and get the JVM version from it.  This can this be used in a Smart Group to point to an EA of the JVM's value, for instance.

Used in:
  * com.github.mlbz521.pkg.AmazonCorrettoOpenJDK


## OfflineApps ##

This was designed for applications that are behind a login or not available via normal internet "acquisitional" methods.

This processor allows you to simply drop the vendor provided "media", in the format they provide, into a specifically named directory and the processor will be able to determine which version of the content to "download," even if multiple versions are available.  

The processor originally expected the vendor content to be organized in sub-directories like `<Software Title>-<version>`, however, this is no longer required and the media can be stored in the root of the specified directory, but the naming convention **must** match or problems will occur.

The specified directory can be local to the AutoPkg runner or on a remote host that will be mounted.  _Before_ "downloading" the processor checks the file size and because it subclasses `URLDownloader`, it uses `cURL` to "download" files.
  * Currently the SMB mount logic uses the process in JSSImporter
    * This prerequisite will be removed in the near future
  * _Recommended:_  The SMB server input variables values can be set in your autopkg prefs file instead of in every recipe

This processor was based on work by:
  * Jesse Peterson
    * [SubDirectoryList](https://github.com/facebook/Recipes-for-AutoPkg/blob/master/Shared_Processors/SubDirectoryList.py)
  * Graham R Pugh
    * [SubDirectoryList](https://github.com/autopkg/grahampugh-recipes/tree/master/CommonProcessors)
    * [LocalRepoUpdateChecker](https://github.com/autopkg/grahampugh-recipes/tree/master/CommonProcessors)

Numerous input variable are available to support as many types of scenarios as I could think of:
  * search_path
    * description: Root path to search within
    * required:  True
  * search_string
    * description:  String that will be used to match items in the search_path
    * required:  True
  * major_version
    * description:  The major version that will be used to match items in the search_path
    * required:  False
  * exception_string
    * description:  String will exclude items from matching the search
    * required:  False
  * limitation_string
    * description:  String that will further limit matching the search
    * required:  False
  * version_separator
    * description:  Character used to separate the "Software Title Name" from the "Version" 
      * For example:  CrowdStrike Falcon-5.27.10803.0'
        * The hyphen would be the separator character 
    * default:  `-`
    * required:  False
  * max_depth
    * description:  Maximum depth of folders to iterate through
    * default:  `1`
    * required:  False
  * OFFLINEAPPS_SMB_URL
    * description:  An optional SMB URL to mount containing the search path
    * required:  False
  * OFFLINEAPPS_SMB_SHARE_NAME
    * description:  Share to mount from the SMB server
    * required:  False
  * OFFLINEAPPS_SMB_PORT
    * description:  Port to use to connect to the SMB server
    * default:  `445`
    * required:  False
  * OFFLINEAPPS_SMB_MOUNT_POINT
    * description:  Where the SMB share will be mounted too
    * default:  `/tmp/OfflineApps/`
    * required:  False
  * OFFLINEAPPS_SMB_USERNAME
    * description:  Username required to connect to the SMB server
    * required:  False
  * OFFLINEAPPS_SMB_PASSWORD
    * description:  Password required to connect to the SMB server
    * required:  False
  * OFFLINEAPPS_SMB_DOMAIN
    * description:  Domain, if required, to connect to the SMB server
    * required:  False

The output variables are:
  * version
    * description:  The highest version found according to pkg_resources.parse_version logic
  * found_major_version
    * description:  The "major version" of the version string found
  * cached_path
    * description:  Path to the existing contents in the AutoPkg Cache, whether newly or previously downloaded
  * download_changed
    * description:  Boolean indicating if the download has changed since the last time it was downloaded

Used in:
  * com.github.mlbz521.download.ARCHICAD
  * com.github.mlbz521.download.AutoCAD
  * com.github.mlbz521.download.BomgarConsole
  * com.github.mlbz521.download.BomgarJumpClient
  * com.github.mlbz521.download.CiscoJabber
  * com.github.mlbz521.download.CrowdStrikeFalconOffline
  * com.github.mlbz521.download.CXoneSoftphone
  * com.github.mlbz521.download.iManageWork
  * com.github.mlbz521.download.JamfProTools
  * com.github.mlbz521.download.JMP
  * com.github.mlbz521.download.Maple
  * com.github.mlbz521.download.Mathematica
  * com.github.mlbz521.download.Matlab
  * com.github.mlbz521.download.Matlab-ISO
  * com.github.mlbz521.download.MatlabUpdate
  * com.github.mlbz521.download.SPSSStatistics


## RicohPrintDriverProcessor ##

This processor finds the download URL for the latest Driver package based on the override-able parameters.

Notables:
  * This Processor inherits from the SeleniumWebScrapper Processor
  * The processor has only been tested against a few different printer models so far.  Additional adjustments may be needed for other models
  * This processor could be tweaked to support Linux, macOS, _and_ Windows (didn't spend the time on this yet)
  * See the requirements for the SeleniumWebScrapper Processor

Input Variables:
  * model:
    * description:  The official model name of the Ricoh Printer to search for
    * required:  True
    * example:  'SP C830DN'
  * os_version
    * description:  The OS version to search against
    * required:  False
    * default:  'latest'
    * options:
      * latest
        * Setting the OS_VERSION key to latest will default to the latest version of macOS **supported by the Processor**
      * Monterey
      * Big Sur
      * Catalina
      * Mojave
      * High Sierra
      * Sierra
  * web_driver
    * description:  The web driver engine to use
    * required:  False
    * default:  Chrome
  * web_driver_path
    * description:  The OS version to search against
    * required:  False
    * default:  $PATH

Used in:
  * com.github.mlbz521.download.RicohPrintDriver


## SeleniumWebScrapper ##

Creates a Context Manager for Selenium to interact with a WebDriver Engine.  Not intended for direct use.

Notables:
  * Requires the [Selenium Library](https://www.selenium.dev/documentation/) and a browser driver to be supplied along with the browser application itself
    * Only support for the ChromeDriver has been added at this time, but support for others can be added with minimal effort
      * Available browser drivers can be found [here](https://www.selenium.dev/downloads/#:~:text=Browsers)
    * To install Selenium in the expected location for this processor, run:
      * `sudo pip3 install --target=/Library/AutoPkg/Selenium selenium`

Used in:
  * CanonPrintDriverProcessor
  * PharosProcessor
  * RicohPrintDriverProcessor

## StringRightSplitter ##

This processor splits a string starting from the right. Uses the "rsplit()" function.

The processor will verify that the occurrence and index input variables are integers and if not, set them as integers.  This was done since most people use key/string pairs and not key/integers.

Used in:
  * com.github.mlbz521.download.Maple
  * com.github.mlbz521.download.SPSSStatistics
  * com.github.mlbz521.jss.XcodeCLITools
  * com.github.mlbz521.pkg.BomgarJumpClient
  * com.github.mlbz521.pkg.CiscoUmbrellaRoamingClient
  * com.github.mlbz521.pkg.RicohPrintDriver


## TextFileReader ##

This processor reads a text file and looks for a regex pattern and returns the rest of the line that matched the pattern.  Source path can be a .dmg which will be mounted.

Used in:
  * com.github.mlbz521.pkg.ARCHICADPatch
  * com.github.mlbz521.pkg.ARCHICAD
  * com.github.mlbz521.pkg.AndroidStudioSDKCLITools


## VersionMajorMinor ##

This processor splits a version string into only the 'Major.Minor' numerals.
  * Expected format is Semantic Versioning
  * Default behavior example: "3.6.5" --> "3.6"

Used in:
  * 


## VersionSubstituter ##

This processor substitutes character(s) in a string by number of occurrences.  You can supply the character to substitutes and the character that will be used in place.
  * By default, it splits using a dash only the first item
  * Default behavior example: "3.0.8-2" --> "3.0.8b2"

Used in:
  * com.github.mlbz521.pkg.ARCHICADPatch
  * com.github.mlbz521.pkg.ARCHICAD


## XarExtractSingleFile ##

Extracts a single file from an archive using xar.  Archive path can be within a .dmg which will be mounted.

Used in:
  * com.github.mlbz521.download.CiscoJabber
  * com.github.mlbz521.download.JMP
  * com.github.mlbz521.download.SetALight3D
  * com.github.mlbz521.pkg.iManageWork
  * com.github.mlbz521.pkg.RicohPrintDriver
  * com.github.mlbz521.pkg.XcodeCLITools


## XPathParser ##

Parses a XML file to pull the desired info using XPath.

Used in:
  * com.github.mlbz521.download.CiscoJabber
  * com.github.mlbz521.download.JMP
  * com.github.mlbz521.download.SetALight3D
  * com.github.mlbz521.pkg.iManageWork
  * com.github.mlbz521.pkg.RicohPrintDriver
  * com.github.mlbz521.pkg.XcodeCLITools


## XPathParserRegEx ##

Parses a XML file to pull the desired info using XPath and provides a method to support parsing element attributes via RegEx.

Used in:
  * com.github.mlbz521.download.CanonPrintDriver
