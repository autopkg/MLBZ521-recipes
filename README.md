mlbz521-recipes
======

Recipes I have created that were not publicly available in other repositories or are unique enough to warrant a second recipe (very rare or unintentionally created around the same time or before being merged into the autopkg org).

I have a number of recipes that use an "offline repository" method.  Basically, these software titles are not available to be downloaded publicly, normally requiring a login to access the download.  So I have written a custom processor that will allow you to simply drop the vendor provided "package", in the format they provide, into a specifically named folder structure, whether local to the system running autopkg or a remote host that will be mounted, and the recipe will be able to determine which version of the application to "download" even if multiple are available.  For more details, review the Shared Processors README linked below.


## Shared Processors ##

A separate README is available for my [shared processors](https://github.com/autopkg/MLBZ521-recipes/blob/master/Shared%20Processors/ReadMe.md).


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
    * Default install path is set to:  /Users/Shared/anaconda3 -- adjustable via substitution variable in an override (for use in lab environments)
  * jss


### Android Studio SDK CLI Tools ###

This can be used with or separately from Android Studio, but the recipe will assume usage with Android Studio.

To provide additional configuration options, my [Manage-AndroidSDKCMDLineTools.sh script](https://github.com/MLBZ521/MacAdmin/blob/master/Software/Manage-AndroidSDKCMDLineTools.sh) is available.
  * Great for use in multi-user, lab, and non-admin environments
  * It can perform the following actions:
    * Initial setup/configuration
      * Set environment variables via a LaunchAgent that the GUI Android Studio application can utilize
      * Allow an (almost seamless) first run experience
        * The first run Android Studio Setup Wizard will run, but the environment variables will be used to pre-configure all settings (the JDK and Android versions would need to be pre-configured in the jdk.table.xml to completely skip the first run wizard)
        * The required minimum SDK components must be installed before first launch to support this
      * Accept CLI Tool licenses
    * Configure Android Studio (GUI) updates settings
    * Install SDK Components
    * Perform updates to installed components
  
Available recipe types:
  * download
  * pkg
    * Override variable available:
      * SHARED_PATH
        * This is the path to where you want to "install" the sdk (`/path/to/sdk/location/`)
          * e.g. Default install path is set to:  `/Users/Shared/Android`
            * Great for use in multi-user, lab, and non-admin environments
  * jss


### Apache Ant ###

Parent Recipe:  com.github.n8felton.pkg.Ant

Available recipe types:
  * jss


### ARCHICAD ###

Recipes for both the full version download as well as the latest patch.

Available recipe types:
  * download
    * `ARCHICAD.download` will "download" from a offline repository
    * `ARCHICAD Patch.download` will download the latest patch
      * Variable overrides for:  major_version, localization, and release_type
      * Uses custom processor to download
  * pkg
    * `ARCHICAD.pkg`
      * Variable overrides for:  EDUSERIALNUMBER and EDUUSERID
    * Multiple custom processors used to create packages
  * jss


### AutoCAD for Mac ###

Recipes for both base and patch installers are available.  Download recipe for the base full version expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from AutoDesk for the supplied major version.

There is a **LEGACY** version of the recipes for the 2020 older installer type.

Available recipe types:
  * download
    * `AutoCAD.download` will "download" from a offline repository
    * `AutoCAD Patch.download` will download the latest patch.
      * Variable overrides for:  major_version
      * Uses custom processor to obtain download url
  * pkg
  * jss


### Bomgar ###

Recipes for both the Representative Console and Jump Client are available.  Download recipes expect the installers are available in an "offline repository".

Available recipe types:
  * download
    * recipes will "download" from a offline repository
    * `BomgarConsole.download`
      * Variable overrides for:  CODE_SIGN_IDENTIFIER
  * pkg
  * jss


### Brother Print Drivers ###

Downloads a Brother Printer Driver, Software Package, Utility, or Firmware specified.  Obviously some packages are compatible with different models, but I haven't been able to think of a way to specify this in the name without it being extremely long.  You will need to specify the model specifically for this to work.  This probably isn't the best way to do it, but it works...

Available recipe types:
  * download
    * Variable overrides for:  MODEL, TYPE_REQUEST, and OS_VERSION
  * pkg
  * jss


### Cisco Jabber ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Cisco Umbrella Roaming Client ###

Downloads the latest release of Cisco Umbrella Roaming Client.

Available recipe types:
  * download
  * pkg
  * jss


### CoreShell Helper ###

Downloads the latest release of the CoreShell Helper.

Please note:  if CoreShell Helper has been installed from the vendor’s install .app, this will not update that previous install.  This is due to the fact that the vendor's installation .app installs the bits into the currently logged in users' home directory (so you can’t deploy it without a user logged in).  The autopkg created .pkg will install the bits into non-user space, so it would/could apply to any/all users on a system.

Available recipe types:
  * download
  * pkg
  * jss


### CrowdStrike Falcon ###

Two recipes "types" are available to choice from for CrowdStrike Falcon.
  * The original "offline" recipe requires the installer is available in an "offline repository"
  * A recipe that downloads the agent via CrowdStrike's API

Shortly after creating the offline recipe format that I'm using for other recipes, CrowdStrike completed a feature request we had to make the download available via their API.  I'm leaving the offline recipe format available incase you don't have access to the API or prefer to not use it.

Available recipe types:
  * download
    * `CrowdStrikeFalconOffline.download`
      * will "download" from a offline repository
    * `CrowdStrikeFalcon.download`
      * Input Variable:
        * client_id:
            * required:  True
            * description:  CrowdStrike API Client ID
        * client_secret:
            * required:  True
            * description:  CrowdStrike API Client Secret
        * policy_id:
            * required:  True
            * description:  CrowdStrike Policy ID to get the assigned Sensor version
        * api_region_url:
            * required:  False
            * default:  `https://api.crowdstrike.com`
            * description:  CrowdStrike Region your instance is associated with
  * pkg
    * Input Variable for:  LICENSE_ID
  * jss


### CXone Softphone ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Cytoscape ###

Downloads the latest release of Cytoscape.

Java 11 is _REQUIRED_ to install Cytoscape.  If Java 11 is not pre-installed, the Cytoscape installer process _should_ download and install Java itself.

Be aware the installation .app is NOT SIGNED.

Available recipe types:
  * download
  * pkg
  * jss


### Google Backup and Sync ###

Parent Recipe:  com.github.nstrauss.pkg.BackupandSync

Available recipe types:
  * jss


### Google Drive ###

Downloads the current release of Google Drive.

This recipe differs from the recipe available in wardsparadox-recipes as it uses the static URL instead of the DriveFSURLProvider Processor which redirects to mirrored servers and causes the recipe to register false-positive new versions and download them.

Available recipe types:
  * download
  * pkg
  * jss


### iManage Work ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Jamf Pro Tools ###

Download recipe expects the installer is available in an "offline repository".  This is designed for our "Site Admins" and doesn't include the `Jamf Admin.app` nor `Jamf Imaging.app`.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### JMP/JMP Pro ###

Download recipe expects the installer is available in an "offline repository".  The download and pkg recipes can be used for either JMP or JMP Pro and a unique jss recipe is available for each.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Maple ###

Recipes for both base and patch installers are available.  Download recipe for the base full version expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from Maple for the supplied major version.

Available recipe types:
  * download
    * `Maple.download` will "download" from a offline repository
    * `Maple Patch.download` will download the latest patch for the supplied major version
      * Variable overrides for:  major_version
      * Uses custom processor to obtain download url
  * pkg
  * jss


### Mathematica ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Matlab ###

Recipes for both base and patch installers are available.  Download recipe expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from Maple for the supplied major version.

I attempted to reverse the build-in update mechanism, however, was not successful in determining how the process works.  So offline recipes will have to be used for now.

I license most software separately in my environment and do not use the built licensePath key.  If you want to use the built-in licensePath Key, you'll want to fork this recipe more than likely.

If you want to customize the products that are installed, a copy of an original, albeit old, installer_input.txt is available in the recipe directory.  I've seen people are unable to locate it as it's not included in newer versions even though the documentation points to it.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
    * `Matlab.pkg`
      * Variable overrides for:  INSTALL_INPUT
        * As the name suggests, this the "installer.input" that allows you to customize the install of Matlab.  The available parameters are included in the recipe; customize for your environment.
  * jss


### Mendeley ###

Parent Recipe:  com.github.hansen-m.pkg.Mendeley

Available recipe types:
  * jss


### MiKTeX ###

Downloads the latest release of MiKTeX.

Available recipe types:
  * download
  * pkg
  * jss


### MirrorOp ###

Parent Recipe:  com.github.moofit-recipes.pkg.MirrorOp

Available recipe types:
  * jss


### MySQL Community Server ###

Parent Recipe:  com.github.gerardkok.download.MySQLCommunityServer

Available recipe types:
  * pkg
  * jss


### NoMAD Login AD ###

Parent Recipe:  com.github.peetinc.download.NoMADLoginAD

The pkg recipe differs from the recipe available in nstrauss-recipes in that it downloads NoLoAD from source and performs no customizations.

Available recipe types:
  * pkg
  * jss


### Nvivo ###

Parent Recipe:  com.github.jazzace.pkg.NVivo

Available recipe types:
  * ~~pkg~~
    * My pkg recipe will be deprecated as I'm using jazzace's pkg recipe now
  * jss


### Pharos Popup Client ###

Added `download` and `pkg` recipes originally created by @asemak (asemak-recipes) after his repo was deprecated and archived.

Available recipe types:
  * download
  * pkg
  * jss


### Praat ###

Parent Recipe:  com.github.autopkg.pkg.Praat

Available recipe types:
  * jss


### PhET Lab Simulations ###

#### **DEPRECATED** ####

Downloads the latest version of a specified PhET Lab Simulation and creates a pseudo macOS application wrapper around the .jar Java executable.  Which allows it to be fully inventoried into Jamf Pro like a standard app.  I did my best to create an 'App' that looks half was decent with icons and what not...  Not a graphics person, so that could be improved.

Currently supported:
  * Balloons and Buoyancy

Additional simulation can be added, only what has been requested in my organization, have I added so far.

Available recipe types:
  * download
    * Variable overrides for:  LAB_SIM
    * Uses custom processor to obtain download url and set other environment information used by child recipes
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


### RealVNC ###

Parent Recipe:  com.github.foigus.download.RealVNCViewer

The vendor's CFBundleShortVersionString format is '6.20.113 (r42303)' which isn't accepted by pkgbuild when building the package.  

So I wrote a hacky solution to supply an accept version string to pkgbuild and still retain the "vendor version" that can be used for naming and use within Jamf Pro (Smart Groups, etc).

Available recipe types:
  * pkg
  * jss


### Respondus Lockdown Browser ###

Parent Recipe:  com.github.nstrauss.download.RespondusLockDownBrowserLab

The download recipe requires you to set your Institution ID and Lab Hash.

Because Respondus does silly things by expecting the licencing information in the file name, the pkg recipe performs "package inception" so that the package name visible in Jamf Pro uses a standard naming convention.

Available recipe types:
  * pkg
  * jss


### Safe Exam Browser ###

Parent Recipe:  com.github.aanklewicz.pkg.SEB

Available recipe types:
  * jss


### Screencast-O-Matic ###

The Screencast-O-Matic application (in my opinion) is poorly designed.  The user has to own .app for them to be able to launch it.  So....that said...That means only one user on any system can actually use this app.  I'm trying to get in contact them to figure this out.  This recipe will account for that (i.e. it changes the permissions on the app to the currently logged in user)...so I highly recommend this is used as a Self Service deployment -- if you require it and their is no user logged it, it will fail, or produce undesirable results.

Available recipe types:
  * download
  * pkg
  * jss


### Set.A.Light 3D ###

Downloads the latest release of Set.A.Light 3D from Elixxier.  I have not attempted to license this in an programmatic way yet, so the result will need to be licensed manually.

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


### SPSS Statistics ###

Recipes for both base and patch installers are available.  Download recipe expects the installer is available in an "offline repository".  The download recipe can be used for either the base or patch installers and unique pkg and jss recipes are needed for additional steps.

There is a **LEGACY** version of the recipes for the v26 and older installer type.

(This _only_ applies to the **LEGACY** recipes) In my environment my base package installs to a custom environment (instead of five folders deep), just in case someone has installed SPSS in a different location somehow, in the Patch.pkg recipe, the postinstall script that "handles the upgrade" searches the `/Applications` folder for the version of SPSS being upgraded and will inject the path into the install.properties file so it does not need to be specified in the INSTALL_PROPERTIES override variable below, which is described below.

Available recipe types:
  * download
    * "download" from a offline repository
  * pkg 
    * (**LEGACY**) Variable overrides for:
      * INSTALL_PROPERTIES
        * As the name suggests, this the "installer.properties" that allows you to customize the install of SPSS.  The available parameters are included; customize for your environment.
      * INSTALL_JDK_CLI
        * A JDK is required to install SPSS silently; if one is not installed, you can provide a command line command to acquire one through any method that is support in your environment
  * jss


### Steam ###

Parent Recipe:  com.github.moofit-recipes.pkg.Steam

Available recipe types:
  * jss


### Tableau Public ###

Parent Recipe:  com.github.foigus.download.tableau-public

Available recipe types:
  * pkg
  * jss


### Twine2 ###

Parent Recipe:  com.github.denmoff.pkg.Twine2

Available recipe types:
  * jss


### VOSviewer ###

Downloads the latest release of VOSviewer.

Java is *REQUIRED* to open VOSviewer.  Amazon's Corretto JDK is not compatiable in my testing.

Be aware the .app is NOT SIGNED.

Available recipe types:
  * download
  * pkg
  * jss


### Xcode IDE ###

Download the Xcode IDE from the Apple dev portal, creates a .pkg, and uploads it to the JPS.

The Policy will be named "%NAME% %Major Version%", e.g. "Xcode 12"

Important Override Variables:
  * You must override APPLE_ID and ( PASSWORD_FILE or PASSWORD )
  * BETA must either be empty for stable releases or set to "Beta" in order to match Xcode betas

See [Facebook's README](https://github.com/facebook/Recipes-for-AutoPkg/tree/master/Xcode) for more information.

To provide additional configuration options, my [Setup-Xcode.sh script](https://github.com/MLBZ521/MacAdmin/blob/master/Software/Setup-Xcode.sh) is available.
  * Great for use in multi-user, lab, and non-admin environments
  * It can perform the following initial setup/configuration options:
    * Specify whether or not to rename the Xcode.app bundle
    * Specify setting developer permissions
      * Optional configurations available
    * Specify whether or not to allow any member of the _developer group to install Apple-provided software
    * Specifies the version of Xcode to use
    * Enables _developer group members to be able to use the debugger or performance analysis tools without authenticating
    * Accept licenses
    * Perform first launch actions

Parent Recipes:
  * com.facebook.autopkg.xcode.downloader
  * com.facebook.autopkg.xcode.extract
  * com.github.moofit-recipes.pkg.Xcode

Available recipe types:
  * jss


### Xcode Command Line Tools ###

Downloads the Xcode Command Line Tools from the Apple dev portal, creates a .pkg, and uploads it to the JPS.  Uses Facebook's "xcode.downloader" recipe.

The Policy will be named "%NAME% %Major Version%", e.g. "Xcode Command Line Tools 12"

Important Override Variables:
  * You must override APPLE_ID and ( PASSWORD_FILE or PASSWORD )
  * BETA must either be empty for stable releases or set to "Beta" in order to match Xcode betas

See [Facebook's README](https://github.com/facebook/Recipes-for-AutoPkg/tree/master/Xcode) for more information.

Parent Recipes:
  * com.facebook.autopkg.xcode.downloader

Available recipe types:
  * pkg
  * jss


### Xerox Print Drivers ###

Downloads the latest Xerox package based on the override-able parameters:  model, download type, and OS Version.  Examples are:
  * "macOS Print and Scan Driver Installer" (default)
  * "ICA Scan USB Driver"
  * "IMAC CA Scan USB Driver"
  * "TWAIN Scan Driver"

Tested both "macOS Print and Scan Driver Installer" and "ICA Scan USB Driver" to download and package successfully.

The "macOS Print and Scan Driver Installer" seems to support a large number of printers through my poking.  So the recipes end up labeling the produced package as such and not for a "unique" printer model (this is a change after the last update).  If you end up choosing a different download type, I would recommend changing the NAME input variable to differentiate from other download types, if you use multiple.

Available recipe types:
  * download
    * Variable overrides for:  model, downloadType, and osVersion
  * pkg
  * jss


### Zoom for IT ###

Downloads the latest version of Zoom for IT Admins package.  This version of the Zoom installer is for customizing the package at install (e.g. SSO, etc.).

Available recipe types:
  * download
  * pkg
    * Variable overrides for: 
      * CONFIG_PLIST
        * Configure Zoom for your organization with the CONFIG_PLIST Key
  * jss


### Zoom Outlook Plugin ###

Recipes for the Zoom Outlook Plugin for macOS.

Available recipe types:
  * download
  * pkg
  * jss
