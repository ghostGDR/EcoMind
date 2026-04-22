#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const execa = require('execa');
const path = require('path');
const fs = require('fs');

const PROJECT_ROOT = path.join(__dirname, '..');

program
  .name('ecomind')
  .description('EcoMind - AI E-commerce Expert')
  .version('1.0.0');

program
  .command('start')
  .description('Start the EcoMind AI server')
  .option('-p, --port <number>', 'Port to run the server on', '8080')
  .action(async (options) => {
    console.log(chalk.blue.bold('\n🚀 EcoMind AI System is starting...\n'));

    const spinner = ora();

    try {
      // 1. Check Python
      spinner.start('Checking Python environment...');
      let pythonCmd = 'python3';
      try {
        await execa('python3', ['--version']);
      } catch (e) {
        try {
          await execa('python', ['--version']);
          pythonCmd = 'python';
        } catch (e2) {
          spinner.fail('Python 3 not found. Please install Python 3.');
          process.exit(1);
        }
      }
      const { stdout: pythonVersion } = await execa(pythonCmd, ['--version']);
      spinner.succeed(`Found ${pythonVersion}`);

      // 2. Setup Virtual Environment
      const venvDir = '.venv';
      const venvPath = path.join(PROJECT_ROOT, venvDir);
      if (!fs.existsSync(venvPath)) {
        spinner.start('Creating virtual environment (this may take a few seconds)...');
        await execa(pythonCmd, ['-m', 'venv', venvDir], { cwd: PROJECT_ROOT });
        spinner.succeed('Virtual environment created');
      }

      // 3. Install Dependencies
      const isWin = process.platform === 'win32';
      const pythonExe = isWin ? path.join(venvDir, 'Scripts', 'python.exe') : path.join(venvDir, 'bin', 'python');
      const pipExe = isWin ? path.join(venvDir, 'Scripts', 'pip.exe') : path.join(venvDir, 'bin', 'pip');
      const fullPythonPath = path.join(PROJECT_ROOT, pythonExe);
      const fullPipPath = path.join(PROJECT_ROOT, pipExe);

      spinner.start('Checking/Installing dependencies (this may take a minute)...');
      await execa(fullPipPath, ['install', '-r', 'requirements.txt'], { cwd: PROJECT_ROOT });
      spinner.succeed('Dependencies ready');

      // 4. Start Server
      spinner.info(`Starting FastAPI server on port ${options.port}...`);
      console.log(chalk.gray('---------------------------------------------------------'));
      
      const serverProcess = execa(fullPythonPath, [
        '-m', 'uvicorn', 'src.api.main:app', 
        '--host', '0.0.0.0', 
        '--port', options.port
      ], {
        cwd: PROJECT_ROOT,
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
        stdio: 'inherit'
      });

      await serverProcess;
    } catch (error) {
      spinner.fail('Startup failed');
      console.error(chalk.red(`\nError: ${error.message}`));
      process.exit(1);
    }
  });

program.parse();
