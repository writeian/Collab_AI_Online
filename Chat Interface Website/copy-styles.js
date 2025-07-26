#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🎨 Chat Interface Style Copier');
console.log('===============================\n');

// Files to copy
const filesToCopy = [
  {
    source: 'styles/globals.css',
    destination: 'src/styles/globals.css',
    description: 'Main CSS with design tokens and theming'
  },
  {
    source: 'components/utils.ts',
    destination: 'src/lib/utils.ts',
    description: 'Utility functions for styling'
  }
];

// Directories to copy
const dirsToCopy = [
  {
    source: 'components/ui',
    destination: 'src/components/ui',
    description: 'shadcn/ui components'
  }
];

console.log('📋 Files to copy:');
filesToCopy.forEach(file => {
  console.log(`  ✅ ${file.source} → ${file.destination}`);
  console.log(`     ${file.description}`);
});

console.log('\n📁 Directories to copy:');
dirsToCopy.forEach(dir => {
  console.log(`  ✅ ${dir.source} → ${dir.destination}`);
  console.log(`     ${dir.description}`);
});

console.log('\n📦 Required npm packages:');
console.log('  npm install tailwindcss @tailwindcss/typography');
console.log('  npm install lucide-react');
console.log('  npm install class-variance-authority clsx tailwind-merge');
console.log('  npm install tailwindcss-animate');

console.log('\n🔧 shadcn/ui components to install:');
console.log('  npx shadcn@latest add avatar');
console.log('  npx shadcn@latest add badge');
console.log('  npx shadcn@latest add button');
console.log('  npx shadcn@latest add input');
console.log('  npx shadcn@latest add card');
console.log('  npx shadcn@latest add separator');

console.log('\n📝 Next steps:');
console.log('1. Create your new project directory');
console.log('2. Copy the files listed above');
console.log('3. Install the required packages');
console.log('4. Setup shadcn/ui with: npx shadcn@latest init');
console.log('5. Install the required components');
console.log('6. Update your imports to match the new file structure');

console.log('\n🎯 Key styling patterns to remember:');
console.log('- Use semantic color tokens (bg-background, text-foreground, etc.)');
console.log('- Layout with flexbox: size-full flex bg-background');
console.log('- Sidebar: w-80 bg-card border-r border-border');
console.log('- Interactive states: hover:bg-accent/50 transition-colors');
console.log('- Spacing: p-4 for padding, gap-3 for gaps');

console.log('\n✨ You\'re all set to use this beautiful design system!'); 