import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Build configurations for each target
const buildTargets = [
  { platform: 'win32', arch: 'x64', name: 'Windows x64' },
  { platform: 'win32', arch: 'arm64', name: 'Windows ARM64' },
  { platform: 'darwin', arch: 'x64', name: 'macOS Intel' },
  { platform: 'darwin', arch: 'arm64', name: 'macOS Apple Silicon' },
  { platform: 'linux', arch: 'x64', name: 'Linux x64' },
  { platform: 'linux', arch: 'x64', name: 'Linux DEB', maker: 'deb' }
];

// Color output functions
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function formatBytes(bytes) {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Byte';
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function getFolderSize(folderPath) {
  let size = 0;
  
  function calculateSize(dirPath) {
    try {
      const files = fs.readdirSync(dirPath);
      
      for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          calculateSize(filePath);
        } else {
          size += stats.size;
        }
      }
    } catch (error) {
      // Ignore errors (e.g., permission denied)
    }
  }
  
  calculateSize(folderPath);
  return size;
}

async function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    log(`Running: ${command} ${args.join(' ')}`, colors.cyan);
    
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      ...options
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

async function buildTarget(target) {
  try {
    log(`\n${colors.bright}Building ${target.name}...${colors.reset}`);
    
    const args = ['run', 'make'];
    
    // Add platform and arch arguments
    if (target.platform) {
      args.push('--', '--platform', target.platform);
    }
    if (target.arch) {
      args.push('--arch', target.arch);
    }
    
    await runCommand('npm', args);
    
    // Check build size
    const outDir = path.join(__dirname, 'out');
    if (fs.existsSync(outDir)) {
      const buildDirs = fs.readdirSync(outDir).filter(dir => {
        const fullPath = path.join(outDir, dir);
        return fs.statSync(fullPath).isDirectory();
      });
      
      for (const buildDir of buildDirs) {
        const buildPath = path.join(outDir, buildDir);
        const size = getFolderSize(buildPath);
        const sizeFormatted = formatBytes(size);
        
        if (size > 200 * 1024 * 1024) { // 200MB in bytes
          log(`⚠️  ${target.name} build size: ${sizeFormatted} (exceeds 200MB)`, colors.yellow);
        } else {
          log(`✅ ${target.name} build size: ${sizeFormatted}`, colors.green);
        }
      }
    }
    
    log(`✅ ${target.name} build completed`, colors.green);
    
  } catch (error) {
    log(`❌ ${target.name} build failed: ${error.message}`, colors.red);
    throw error;
  }
}

async function optimizeNodeModules() {
  log('\n🧹 Optimizing node_modules...', colors.yellow);
  
  try {
    // Clean npm cache only (keep dev dependencies for building)
    await runCommand('npm', ['cache', 'clean', '--force']);
    
    log('✅ Node modules optimized', colors.green);
  } catch (error) {
    log(`⚠️  Node modules optimization failed: ${error.message}`, colors.yellow);
  }
}

async function cleanOutput() {
  log('🧹 Cleaning previous builds...', colors.yellow);
  
  try {
    await runCommand('npm', ['run', 'clean']);
    log('✅ Previous builds cleaned', colors.green);
  } catch (error) {
    log(`⚠️  Clean failed: ${error.message}`, colors.yellow);
  }
}

async function main() {
  log(`${colors.bright}${colors.blue}Isle Nova - Multi-Platform Build Script${colors.reset}`);
  log(`Building for: ${buildTargets.map(t => t.name).join(', ')}\n`);
  
  const startTime = Date.now();
  
  try {
    // Clean previous builds
    await cleanOutput();
    
    // Optimize dependencies
    await optimizeNodeModules();
    
    // Build each target
    for (const target of buildTargets) {
      await buildTarget(target);
    }
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000 / 60).toFixed(2);
    
    log(`\n${colors.bright}${colors.green}🎉 All builds completed successfully!${colors.reset}`);
    log(`Total build time: ${duration} minutes`);
    
    // Show final output directory
    const outDir = path.join(__dirname, 'out');
    if (fs.existsSync(outDir)) {
      log(`\nBuilds available in: ${outDir}`, colors.cyan);
      
      const builds = fs.readdirSync(outDir).filter(dir => {
        const fullPath = path.join(outDir, dir);
        return fs.statSync(fullPath).isDirectory();
      });
      
      log('\nBuild summary:', colors.bright);
      for (const build of builds) {
        const buildPath = path.join(outDir, build);
        const size = getFolderSize(buildPath);
        const sizeFormatted = formatBytes(size);
        const status = size > 200 * 1024 * 1024 ? '⚠️ ' : '✅';
        log(`  ${status} ${build}: ${sizeFormatted}`);
      }
    }
    
  } catch (error) {
    log(`\n❌ Build process failed: ${error.message}`, colors.red);
    process.exit(1);
  }
}

main();
