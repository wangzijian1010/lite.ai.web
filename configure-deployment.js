#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🚀 Deployment Configuration Helper\n');

rl.question('Enter your backend URL for production (e.g., https://your-backend.com): ', (backendUrl) => {
  if (!backendUrl) {
    console.log('❌ Backend URL is required');
    rl.close();
    return;
  }

  // Validate URL format
  try {
    new URL(backendUrl);
  } catch (error) {
    console.log('❌ Invalid URL format. Please include http:// or https://');
    rl.close();
    return;
  }

  // Update .env.production
  const envProductionPath = path.join(__dirname, 'frontend', '.env.production');
  const envContent = `# Production Environment Configuration
VITE_API_BASE_URL=${backendUrl}

# Generated on ${new Date().toISOString()}
`;

  fs.writeFileSync(envProductionPath, envContent);
  
  console.log('\n✅ Configuration updated successfully!');
  console.log(`📝 Updated frontend/.env.production with: ${backendUrl}`);
  console.log('\n📋 Next steps:');
  console.log('1. Make sure your backend CORS allows your frontend domain');
  console.log('2. Run "npm run build" in the frontend directory');
  console.log('3. Test the build with "npm run preview"');
  console.log('4. Deploy your application');
  
  rl.close();
});