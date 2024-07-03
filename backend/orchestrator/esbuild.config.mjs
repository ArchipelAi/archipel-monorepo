import * as esbuild from 'esbuild';
import copy from 'esbuild-plugin-copy';

await esbuild.build({
  entryPoints: ['src/orchestrator/orchestrator.ts'],
  // entryPoints: ['src/index.ts'],
  bundle: true,
  platform: 'node',
  outfile: 'dist/index.js',
  external: ['@fastify/swagger', '@fastify/swagger-ui'],
  plugins: [
    copy({
      resolveFrom: 'cwd',
      assets: {
        from: ['node_modules/@fastify/swagger-ui/static/*'],
        to: ['dist/static'],
      },
    }),
  ],
});
