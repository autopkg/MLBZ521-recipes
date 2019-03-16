mlbz521-recipes
======

Just a few recipes I have created that were not publicly available in other repositories or are unique enough to warrant a second recipe.

## Recipes ##

### Amazon Corretto OpenJDK ###

Amazon Corretto is an OpenJDK alternative that is maintained and supported by Amazon.  These recipes allow you to specify which version you'd want; currently 8 and 11 are available from Amazon.

Optionally, this package will pull out the JVM Version which can be used with a Smart Group pointing to an extension attribute to determine latest version.  I have an EA available that can be used in conjunction with this recipe.

Available recipe types:
  * download
    * Variable overrides for:  JDK_MAJOR_VERSION
    * Uses custom processor to download
  * pkg
  * jss
    * Use the EXTENSION_ATTRIBUTE override variable to use your current EA.


### Anaconda ###

Parent:  com.github.hansen-m.download.Anaconda

Available recipe types:
  * pkg
    * Variable overrides for version
    * Create a deployable `.pkg` from the `.sh` script installer
    * Default install path is set to:  /Users/Shared/anaconda2 -- adjustable via substitution variable in an override (for use in lab environments)
  * jss


### ARCHICAD ###

Recipes for both the full version download as well as the latest patch.

Available recipe types:
  * download
    * `ARCHICAD.download` will download the latest full installer.
    * `ARCHICAD Patch.download` will download the latest patch.
      * Variable overrides for:  major_version, localization, and release_type
      * Uses custom processor to download
  * pkg
    * `ARCHICAD.pkg`
      * Variable overrides for:  EDUSERIALNUMBER and EDUUSERID
      * Uses multiple custom processor to package
  * jss


### Brother Printer ###

Downloads a Brother Printer Driver, Software Package, Utility, or Firmware specified.  Obviously some packages are compatible with different models, but I haven't been able to think of a way to specify this in the name without it being extremely long.  You will need to specify the model specifically for this to work.  This probably isn't the best way to do it, but it works...

Available recipe types:
  * download
    * Variable overrides for:  MODEL, TYPE_REQUEST, and OS_VERSION
  * pkg
  * jss


### Google Backup and Sync ###

Parent Recipe:  com.github.nstrauss.pkg.BackupandSync

Available recipe types:
  * jss


### Google Drive File Stream ###

Downloads the current release of Google Drive File Stream.

This recipe differs from the recipe available in wardsparadox-recipes as it uses the static URL instead of the DriveFSURLProvider Processor which redirects to mirrored servers and causes the recipe to register false-positive new versions and download them.

Available recipe types:
  * download
  * pkg
  * jss


### Nvivo ###

Parent Recipe:  com.github.joshua-d-miller.download.nvivo
  * Variable overrides for:  MAJOR_VERSION

Available recipe types:
  * pkg
  * jss


### QGIS ###

Downloads the latest specified major_version of QGIS.  Requires python.org Python 3.6 to be pre-installed - other distributions (newer or older) are not supported.  This probably isn't the best way to do it, but it's simple and works for now.

The other publicly available QGIS recipe was no longer functional when the download location moved.  Also added support for different major versions.

Available recipe types:
  * download
    * Variable overrides for:  QGIS_Major_Version
  * pkg
    * Python 3.6+ is a prerequisite before installing QGIS 3 -- the created .pkg will hard fail if Python 3.6+ is not installed.
    * The created .pkg will "uninstall" previous versions of QGIS.
    * The QGIS installer process will also install the necessary Python modules using pip. This requires an internet connection during installation.
  * jss


### Screencast-O-Matic ###

The Screencast-O-Matic application (in my opinion) is poorly designed.  The user has to own .app for them to be able to launch it.  So....that said...That means only one user on any system can actually use this app.  I'm trying to get in contact them to figure this out.  This recipe will account for that (i.e. it changes the permissions on the app to the currently logged in user)...so I highly recommend this is used as a Self Service deployment -- if you require it and their is no user logged it, it will fail, or produce undesirable results.

Available recipe types:
  * download
  * pkg
  * jss


### Solstice ###

Modified from the original author:  [@joshua-d-miller](https://github.com/autopkg/joshua-d-miller-recipes)
This was removed from his recipe list, but I wanted to use it.  The way Mersive creates the distribution package for Solstice is very wacky (a zip, with an .app that creates another .app).

This is v2 of my hack-ish way of being able to deploy this application, but it works. ¯\\_(ツ)_/¯

v1 would do all the work to get the final .app on the client machine, which wasn't exactly desired, while this version will get the final .app on the system running autopkg.
\*\*\*Note this likely requires a user to be logged in when this is ran, as the stupid Solstice bootstrap .app, creates the final .app on the desktop of the user that ran it.
It's dumb, I know.  I've contacted Mersive about it and they claim they're looking at improving macOS deployment in the future, but no ETA.

Hopefully this overhaul will help with the false positives.

Available recipe types:
  * download
  * pkg
  * jss


### Zoom ###

Recipes for both Zoom for IT Admins package and the Zoom Outlook Plugin for macOS.

Available recipe types:
  * download
    * `Zoom-ForIT.download` - Downloads the latest version of Zoom for IT Admins package.  For customizing the package (i.e. SSO, etc)
  * pkg
    * `Zoom-ForIT.pkg` - Variable overrides for: CONFIG_PLIST
      * Configure Zoom for your organization with the CONFIG_PLIST Key
  * jss



## Shared Processors ##

### FileMode ###

This processor essentially runs `chmod` on a file.  Provide the numeric mode for file in octal format.


### JVMVersioner ###

This processor finds the Java Virtual Machine version in a JDK package.  This will allow you to use which OpenJDK distributor you would like, and get the JVM version from it.  This can this be used in a Smart Group point to an EA of the JVM's value, for instance.


### TextFileReader ###

This process reads a text file, which can point to a path inside a .dmg which will be mounted, looks for a regex pattern and returns the rest of the line that matched the pattern.


### VersionMajorMinor ###

This processor splits a version string into only the 'Major.Minor' numerals.
  * Expected format is Semantic Versioning
  * Default behavior example: "3.6.5" --> "3.6"


### VersionSubstituter ###

This processor substitutes character(s) in a string by number of occurrences.
  * By default, it splits using a dash only the first item
  * Default behavior example: "3.0.8-2" --> "3.0.8b2"
