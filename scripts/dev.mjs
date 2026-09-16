import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { createServer } from 'node:net';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const local = process.argv.includes('--local');
const python = resolve(root, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const config = resolve(root, '.env.supabase.development');
const children = [];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill();
  process.exitCode = code;
}
function launch(command, args, env = process.env) {
  const child = spawn(command, args, { cwd: root, env, stdio: 'inherit', windowsHide: true });
  children.push(child);
  child.on('error', error => { console.error(error.message); stop(1); });
  child.on('exit', (code, signal) => {
    if (!stopping) {
      const service = command === python ? 'API' : 'Frontend';
      console.error(`${service} process ${child.pid} exited (code: ${code ?? 'none'}, signal: ${signal ?? 'none'}). Restart with npm run dev.`);
      stop(code || 1);
    }
  });
  return child;
}
async function freePort(port) {
  await new Promise((ok, fail) => {
    const server = createServer();
    server.once('error', () => fail(new Error(`Port ${port} is already occupied. Stop the existing development server before starting both services.`)));
    server.listen(port, '127.0.0.1', () => server.close(ok));
  });
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
try {
  if (!existsSync(python)) throw new Error('Create .venv and install backend/requirements.txt first.');
  if (!local && !existsSync(config)) throw new Error('Missing .env.supabase.development. Supabase configuration is required; no silent fallback to local accounts.');
  await freePort(8000);
  await freePort(5173);
  launch(python, ['-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', '8000', '--no-access-log', ...(!local ? ['--env-file', config] : [])], { ...process.env, AUTH_PROVIDER: local ? 'local' : 'supabase', APP_ORIGIN: 'http://127.0.0.1:5173' });
  let ready = false;
  for (let i = 0; i < 60 && !stopping; i++) {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/options', { signal: AbortSignal.timeout(1000) });
      const options = await response.json();
      if (response.ok && options.managed === !local) { ready = true; break; }
    } catch {}
    await new Promise(done => setTimeout(done, 500));
  }
  if (!ready) throw new Error('API did not become ready with the expected authentication mode. Check the errors above.');
  launch(process.execPath, ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5173', '--strictPort']);
  console.log(`LexVigil ${local ? 'local test' : 'Supabase'} services ready. Open http://127.0.0.1:5173/login. Keep this terminal running; restart this command after reboot.`);
} catch (error) { console.error(error.message); stop(1); }
