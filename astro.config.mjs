import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://Miss-PinkElf.github.io',
  base: '/mine-blog/',
  integrations: [react()],
});
