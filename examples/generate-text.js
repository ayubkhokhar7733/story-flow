import 'dotenv/config';
import { AiHordeClient } from '../src/ai-horde-client.js';

const client = new AiHordeClient();

async function main() {
  const prompt = process.argv[2] || 'In three sentences, explain why open source AI clusters are revolutionary:';

  console.log('🤖 AI Horde Free Text Generation');
  console.log(`Prompt: "${prompt}"`);
  console.log('--------------------------------------------------');

  // Discover best model dynamically
  const bestModel = await client.getBestModel('text', 'koboldcpp/Llama-3.2-3B-Instruct-Q4_K_M');
  console.log(`Using model: ${bestModel}\n`);

  try {
    const result = await client.generateText(
      {
        prompt,
        models: [bestModel],
        params: {
          max_length: 120,
          max_context_length: 1024,
          temperature: 0.7,
        },
      },
      (progress) => {
        if (progress.step === 'submitted') {
          console.log(`[Job Dispatched] ID: ${progress.jobId} (Kudos: ${progress.kudos})`);
        } else if (progress.step === 'polling') {
          process.stdout.write(
            `\r⏳ Polling... Queue pos: ${progress.queue_position ?? 0} | Est. wait: ${progress.wait_time ?? 0}s | Elapsed: ${progress.elapsedSeconds}s   `
          );
        } else if (progress.step === 'completed') {
          process.stdout.write('\r✅ Generation complete!                                                  \n');
        }
      }
    );

    console.log('\n--- Output ---');
    console.log(result.text.trim());
    console.log('--------------');
    console.log(`Worker: ${result.workerName} | Model: ${result.model}`);
  } catch (err) {
    console.error('\n❌ Generation failed:', err.message);
  }
}

main();
