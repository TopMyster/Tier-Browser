import { FusesPlugin } from '@electron-forge/plugin-fuses';
import { FuseV1Options, FuseVersion } from '@electron/fuses';

export default {
  packagerConfig: {
    asar: true,
    name: 'Isle Nova',
    executableName: 'Isle Nova',
    icon: './assets/icon',
    appBundleId: 'com.topmyster.islenovabrowser',
    appCategoryType: 'public.app-category.productivity',
    osxSign: false, 
    osxNotarize: false, 
    win32metadata: {
      CompanyName: 'TopMyster',
      FileDescription: 'Isle Nova Browser',
      OriginalFilename: 'Isle Nova.exe',
      ProductName: 'Isle Nova',
      InternalName: 'Isle Nova'
    }
  },
  rebuildConfig: {},
  makers: [
    // Windows x64
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle.Nova-win32-x64'
      },
      platforms: ['win32']
    },
    // Windows Squirrel installer
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'isle-nova',
        setupExe: 'Isle-Nova-Setup.exe',
        setupIcon: './assets/icon.ico'
      },
      platforms: ['win32']
    },
    // macOS ZIP files
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle.Nova-macOS'
      },
      platforms: ['darwin']
    },
    // Linux DEB package
    {
      name: '@electron-forge/maker-deb',
      config: {
        name: 'isle-nova',
        options: {
          maintainer: 'TopMyster',
          homepage: 'https://github.com/TopMyster/IsleBrowser',
          description: 'A modern, innovative browser built with Electron',
          categories: ['Network', 'WebBrowser'],
          section: 'web',
          priority: 'optional',
          depends: ['libgtk-3-0', 'libxss1', 'libgconf-2-4', 'libnss3']
        }
      },
      platforms: ['linux']
    },
    // Linux ZIP
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle-nova-linux-x64'
      },
      platforms: ['linux']
    }
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
   
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
};
