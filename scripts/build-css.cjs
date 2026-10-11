const { spawnSync } = require('node:child_process');
const { mkdirSync } = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const cli = require.resolve('tailwindcss/lib/cli.js');
mkdirSync(path.join(root, 'assets/css'), { recursive: true });

for (const [config, output] of [
  ['tailwind.config.cjs', 'site.min.css'],
  ['tailwind.default.config.cjs', 'default.min.css'],
]) {
  const result = spawnSync(process.execPath, [cli,
    '--config', config,
    '--input', 'styles/site.css',
    '--output', `assets/css/${output}`,
    '--minify',
  ], { cwd: root, stdio: 'inherit' });
  if (result.status !== 0) process.exit(result.status || 1);
}
