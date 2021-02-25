Shared Processors
======

This readme will give a short description for each processor and which recipes the processor is used in, for examples of use and my sanity if I update one and don't remember where all I've used it.


## AutoDeskPatchProcessor ##

This processor finds the URL for the latest patch of the supplied major version of an AutoDesk product.  Should support all products and major versions.

Used in:
  * com.github.mlbz521.download.AutoCADPatch


## CFBundleInfo ##

Supply a path to a plist file, which can point to a path inside a .dmg which will be mounted, and will returns four output_variables, which you can decide how to use:
  * CFBundleVersion
  * CFBundleShortVersionString
  * CFBundleIdentifier
  * version (CFBundleShortVersionString)

Used in:
  * com.github.mlbz521.pkg.RealVNCViewer
  * com.github.mlbz521.pkg.VOSviewer


## ExtractWith7z ##

This processor extracts files with a specified 7zip binary.

Used in:
  * com.github.mlbz521.download.MaplePatch


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
  * com.github.mlbz521.pkg.SPSSStatisticsLegacy
  * com.github.mlbz521.pkg.SPSSStatisticsPatch


## JVMVersioner ##

This processor finds the Java Virtual Machine version in a JDK package.  This will allow you to use which OpenJDK distribution you would like, and get the JVM version from it.  This can this be used in a Smart Group to point to an EA of the JVM's value, for instance.

Used in:
  * com.github.mlbz521.pkg.AmazonCorrettoOpenJDK


## OfflineApps ##

Used to locate and "download" offline application content that can then be used for child pkg recipes.  This is for applications that are behind a login or not available via normal internet "acquisitional" methods.  This processor was based on work by:
  * Jesse Peterson
    * [SubDirectoryList](https://github.com/facebook/Recipes-for-AutoPkg/blob/master/Shared_Processors/SubDirectoryList.py)
  * Graham R Pugh
    * [SubDirectoryList](https://github.com/autopkg/grahampugh-recipes/tree/master/CommonProcessors)
    * [LocalRepoUpdateChecker](https://github.com/autopkg/grahampugh-recipes/tree/master/CommonProcessors)

Numerous input variable are available to support as many types of scenarios as I could think of:
  * search_path
    * description: 'Root path to search within.
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
    * default': '-'
    * required:  False
  * max_depth
    * description:  Maximum depth of folders to iterate through
    * default': '1'
    * required:  False

The output variables are:
  * version
    * description:  The highest version found according to pkg_resources.parse_version logic
  * cached_path
    * description:  Path to the existing contents in the AutoPkg Cache, whether newly or previously downloaded

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
  * com.github.mlbz521.download.SPSSStatistics


## StringRightSplitter ##

This processor splits a string starting from the right. Uses the "rsplit()" function.

The processor will verify that the occurrence and index input variables are integers and if not, set them as integers.  This was done since most people use key/string pairs and not key/integers.

Used in:
  * com.github.mlbz521.download.Maple
  * com.github.mlbz521.download.SPSSStatistics
  * com.github.mlbz521.pkg.BomgarJumpClient
  * com.github.mlbz521.pkg.CiscoUmbrellaRoamingClient


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

Extracts a single file from an archive using xar.

Used in:
  * com.github.mlbz521.download.CiscoJabber
  * com.github.mlbz521.download.JMP
  * com.github.mlbz521.download.SetALight3D
  * com.github.mlbz521.pkg.iManageWork
  * com.github.mlbz521.pkg.RespondusLockDownBrowserLabEdition


## XPathParser ##

Parses a XML file to pull the desired info using XPath.

Used in:
  * com.github.mlbz521.download.CiscoJabber
  * com.github.mlbz521.download.JMP
  * com.github.mlbz521.download.SetALight3D
  * com.github.mlbz521.pkg.iManageWork
  * com.github.mlbz521.pkg.RespondusLockDownBrowserLabEdition

