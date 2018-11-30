# albumart-dl

Download HQ album cover art from Apple's iTunes.

Automatically downloads the highest resolution, usually up to 3000 x 3000 px. Actual resolutions vary greatly depending on the source material and can go as low as 600 x 600 px.

## Use

```albumart-dl <search-term>```

Example: Download [Frank Zappa's Apostrophe](https://itunes.apple.com/us/album/apostrophe/549280054)

```albumart-dl "Frank Zappa Apostrophe"```

Download album art files to specific folder

```albumart-dl -o <path-to-folder> <search-term>```

Example: Download [all albums by Miles Davis](https://itunes.apple.com/us/artist/miles-davis/44984) to a subfolder

```albumart-dl -o ~/Downloads/"Miles Davis"/ "Miles Davis"```

## Install

```bash
brew tap paulgalow/tap
brew install albumart-dl
```

## Dependencies

albumart-dl requires Python 3.6+. External libraries used are [yaspin](https://github.com/pavdmyt/yaspin) and [requests](https://github.com/requests/requests).