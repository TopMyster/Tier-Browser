const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

// Get the target platform from command line args or use current platform
const getTargetPlatform = () => {
  const args = process.argv;
  const platformIndex = args.findIndex(arg => arg === '--platform');
  return platformIndex !== -1 && args[platformIndex + 1] ? args[platformIndex + 1] : process.platform;
};

const targetPlatform = getTargetPlatform();

module.exports = {
  packagerConfig: {
    asar: true,
    name: 'Isle Nova',
    executableName: 'Isle Nova',
    icon: './assets/icon',
    appBundleId: 'com.topmyster.islenovabrowser',
    appCategoryType: 'public.app-category.productivity',
    osxSign: false, 
    osxNotarize: false,
    // Size optimization settings - being more conservative to avoid breaking dependencies
    ignore: [
      // Test directories and files
      /\/node_modules\/.*\/test\//,
      /\/node_modules\/.*\/tests\//,
      /\/node_modules\/.*\/__tests__\//,
      /\/node_modules\/.*\/.*\.spec\.(js|ts|jsx|tsx)$/,
      /\/node_modules\/.*\/.*\.test\.(js|ts|jsx|tsx)$/,
      
      // Documentation and examples
      /\/node_modules\/.*\/example\//,
      /\/node_modules\/.*\/examples\//,
      /\/node_modules\/.*\/docs?\//,
      /\/node_modules\/.*\/demo\//,
      /\/node_modules\/.*\/demos\//,
      
      // VCS files
      /\/node_modules\/.*\/.git\//,
      /\/node_modules\/.*\/\.travis\.yml$/,
      
      // Documentation files
      /\/node_modules\/.*\/README\.(md|txt|rst)$/i,
      /\/node_modules\/.*\/CHANGELOG\.(md|txt|rst)$/i,
      /\/node_modules\/.*\/LICENSE/i,
      
      // Source maps
      /\/node_modules\/.*\/.*\.map$/
    ],
    // Include only English locale to save space
    afterCopy: [(buildPath, electronVersion, platform, arch, callback) => {
      const fs = require('fs');
      const path = require('path');
      
      const localesPath = path.join(buildPath, 'locales');
      if (fs.existsSync(localesPath)) {
        const files = fs.readdirSync(localesPath);
        files.forEach(file => {
          if (!file.startsWith('en-US') && file.endsWith('.pak')) {
            try {
              fs.unlinkSync(path.join(localesPath, file));
            } catch (e) {
              // Ignore errors
            }
          }
        });
      }
      callback();
    }],
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
      platforms: ['win32'],
      arch: ['x64']
    },
    // Windows ARM64
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle.Nova-win32-arm64'
      },
      platforms: ['win32'],
      arch: ['arm64']
    },
    // macOS Intel (x64)
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle.Nova-macOS-intel'
      },
      platforms: ['darwin'],
      arch: ['x64']
    },
    // macOS ARM64
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle.Nova-macOS-arm64'
      },
      platforms: ['darwin'],
      arch: ['arm64']
    },
    // Linux DEB package
    {
      name: '@electron-forge/maker-deb',
      config: {
        name: 'Isle-nova-1.0.0-amd64.deb',
        options: {
          bin: 'Isle Nova',
          maintainer: 'TopMyster',
          homepage: 'https://github.com/TopMyster/IsleBrowser',
          description: 'A modern, innovative browser built with Electron',
          categories: ['Network', 'WebBrowser']
        }
      },
      platforms: ['linux'],
      arch: ['x64']
    },
    // Linux ZIP
    {
      name: '@electron-forge/maker-zip',
      config: {
        name: 'Isle-nova-1.0.0-linux-x64'
      },
      platforms: ['linux'],
      arch: ['x64']
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
