import { copyFileSync, mkdirSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(rootDir, '../..')

function syncScreenParameters(): Plugin {
  const source = path.join(repoRoot, 'pipeline', 'SCREEN_PARAMETERS.md')
  const destDir = path.join(rootDir, 'src', 'content')
  const dest = path.join(destDir, 'screen-parameters.md')

  const copy = () => {
    mkdirSync(destDir, { recursive: true })
    copyFileSync(source, dest)
  }

  return {
    name: 'sync-screen-parameters',
    buildStart() {
      copy()
    },
    configureServer(server) {
      copy()
      server.watcher.add(source)
      server.watcher.on('change', (file) => {
        if (path.resolve(file) === path.resolve(source)) copy()
      })
    },
  }
}

// GitHub Pages project site base path
export default defineConfig({
  plugins: [react(), syncScreenParameters()],
  base: process.env.VITE_BASE ?? '/stock-trader/',
})
