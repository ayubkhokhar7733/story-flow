import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';
import { AiHordeClient } from '../src/ai-horde-client.js';

const client = new AiHordeClient();

async function main() {
  const prompt = process.argv[2] || 'A cinematic hyperrealistic shot of a cyberpunk city floating among glowing neon clouds, 8k resolution, octane render';
  const model = process.argv[3] || 'stable_diffusion';

  console.log('🎨 AI Horde Free Image Generation');
  console.log(`Prompt: "${prompt}"`);
  console.log(`Model: ${model}`);
  console.log('Parameters: 512x512, 20 steps, k_euler_a, CFG 7.5 (Free tier optimized)');
  console.log('--------------------------------------------------');

  try {
    const result = await client.generateImage(
      {
        prompt,
        models: [model],
        params: {
          width: 512,
          height: 512,
          steps: 20,
          sampler_name: 'k_euler_a',
          cfg_scale: 7.5,
        },
        nsfw: false,
        censor_nsfw: true,
        r2: true,
      },
      (progress) => {
        if (progress.step === 'submitted') {
          console.log(`[Job Dispatched] ID: ${progress.jobId} (Kudos: ${progress.kudos})`);
        } else if (progress.step === 'polling') {
          process.stdout.write(
            `\r⏳ Polling... Queue pos: ${progress.queue_position ?? 0} | Est. wait: ${progress.wait_time ?? 0}s | Processing: ${progress.processing} | Elapsed: ${progress.elapsedSeconds}s   `
          );
        } else if (progress.step === 'finishing') {
          process.stdout.write('\r⚡ Job finished processing! Retrieving asset...                          \n');
        } else if (progress.step === 'completed') {
          process.stdout.write('✅ Image ready!\n');
        }
      }
    );

    console.log('\n--- Result ---');
    console.log(`Job ID:      ${result.id}`);
    console.log(`Model:       ${result.model}`);
    console.log(`Worker:      ${result.workerName}`);
    console.log(`Seed:        ${result.seed}`);
    console.log(`Image Asset: ${result.imageUrl}`);

    // If base64 or URL, optionally save a copy locally
    if (result.imageUrl.startsWith('http')) {
      console.log(`\nDirect Image URL:\n${result.imageUrl}`);
    } else {
      // Base64 image
      const outputDir = path.resolve('output');
      await fs.mkdir(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, `${result.id}.webp`);
      await fs.writeFile(outputPath, Buffer.from(result.imageUrl, 'base64'));
      console.log(`Saved locally to: ${outputPath}`);
    }
  } catch (err) {
    console.error('\n❌ Generation failed:', err.message);
  }
}

main();
