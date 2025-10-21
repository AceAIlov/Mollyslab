import 'dotenv/config';
import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import fetch from 'cross-fetch';

const RPC_URL = process.env.RPC_URL || 'http://127.0.0.1:8899';
const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY || '';
const CLAUDE_MODEL = process.env.CLAUDE_MODEL || 'claude-3-5-sonnet-20240620';

if (!CLAUDE_API_KEY) console.warn('⚠️ CLAUDE_API_KEY missing — mock signals only.');

const Strategy = { Momentum: 0, Arbitrage: 1, Lp: 2, MeanReversion: 3 } as const;
const Side = { Long: 0, Short: 1 } as const;

type StrategyKey = keyof typeof Strategy;

type Signal = {
  assetMint: string;
  strategy: StrategyKey;
  direction: keyof typeof Side;
  confidenceBps: number;
  notional: number;
  price: number;
};

async function claudeSignal(prompt: string): Promise<Signal> {
  if (!CLAUDE_API_KEY) {
    return { assetMint: Keypair.generate().publicKey.toBase58(), strategy: 'Momentum', direction: 'Long', confidenceBps: 9000, notional: 1000, price: 100 };
  }
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': CLAUDE_API_KEY, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({ model: CLAUDE_MODEL, max_tokens: 200, messages: [{ role: 'user', content: prompt }] })
  });
  const json = await res.json();
  const text: string = json?.content?.[0]?.text || '';
  const mint = text.match(/mint:([1-9A-HJ-NP-Za-km-z]{32,44})/)?.[1] || Keypair.generate().publicKey.toBase58();
  return { assetMint: mint, strategy: 'Momentum', direction: 'Long', confidenceBps: 9000, notional: 1000, price: 100 };
}

(async () => {
  const connection = new Connection(RPC_URL, 'confirmed');
  const wallet = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(require('fs').readFileSync(process.env.WALLET || `${process.env.HOME}/.config/solana/id.json`, 'utf8')))
  );

  console.log('🔮 Generating signal with Claude…');
  const signal = await claudeSignal('Generate a high-confidence SOL momentum signal. Output minimal JSON.');
  console.log('✅ Signal', signal);

  const assetMint = new PublicKey(signal.assetMint);
  const { spawnSync } = require('child_process');
  const exec = spawnSync(
    './target/release/molly',
    ['execute', '--strategy', signal.strategy.toLowerCase(), assetMint.toBase58(), signal.direction.toLowerCase(), String(signal.confidenceBps), String(signal.notional), String(signal.price)],
    { stdio: 'inherit' }
  );
  if (exec.status !== 0) process.exit(exec.status || 1);
  console.log('📈 Execution recorded on-chain (simulated PnL).');
})();
