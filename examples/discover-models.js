import 'dotenv/config';
import { AiHordeClient } from '../src/ai-horde-client.js';

const client = new AiHordeClient();

async function main() {
  console.log('🔍 Fetching active AI Horde models...\n');

  try {
    const [imageModels, textModels] = await Promise.all([
      client.getActiveImageModels(),
      client.getActiveTextModels(),
    ]);

    console.log(`=== Top 10 Active Image Models (Total Active: ${imageModels.length}) ===`);
    imageModels.slice(0, 10).forEach((m, idx) => {
      console.log(`${idx + 1}. [${m.count} workers | ETA: ${m.eta}s] ${m.name}`);
    });

    console.log(`\n=== Top 10 Active Text Models (Total Active: ${textModels.length}) ===`);
    textModels.slice(0, 10).forEach((m, idx) => {
      console.log(`${idx + 1}. [${m.count} workers | ETA: ${m.eta}s] ${m.name}`);
    });
  } catch (err) {
    console.error('❌ Error discovering models:', err.message);
  }
}

main();
