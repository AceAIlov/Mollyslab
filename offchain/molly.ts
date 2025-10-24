// offchain/molly.ts
// Unified dev CLI: --chain sol | bnb
// Sol → spawns Rust 'molly' binary; BNB → uses ethers to call Router/Slab.

import 'dotenv/config';
import { spawnSync } from 'node:child_process';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

import { ethers } from 'ethers';

const argv = await yargs(hideBin(process.argv))
  .scriptName('mollyx')
  .option('chain', { type: 'string', choices: ['sol', 'bnb'], default: 'sol', describe: 'Target chain' })
  .command('whoami', 'Show identity & cluster/endpoint')
  .command('init [admin] [oracle] [threshold]', 'Solana: initialize router', (y) =>
    y.positional('admin', { type: 'string' })
     .positional('oracle', { type: 'string' })
     .positional('threshold', { type: 'number', default: 7000 }))
  .command('pause <paused>', 'Solana: pause/unpause', (y) =>
    y.positional('paused', { type: 'boolean' }))
  .command('threshold <bps>', 'Solana: update threshold', (y) =>
    y.positional('bps', { type: 'number' }))
  .command('oracle-set <asset> <score>', 'Set oracle score (Sol: router; BNB: Router.setOracleScore)', (y)=>y)
  .command('mandate-mint <asset> <strategy> [ttl]', 'Mint mandate (Sol/BNB)', (y) =>
    y.positional('ttl', { type: 'number', default: 300 }))
  .command('deploy <strategy>', 'Deploy slab (Sol) / init slab (BNB)', (y)=>y)
  .command('execute <strategy> <asset> <dir> <conf> <notional> <price>', 'Execute trade signal', (y)=>y)
  .command('revoke <user> <asset> <strategy>', 'Revoke mandate (Sol) / by admin or user (BNB)', (y)=>y)
  .command('status', 'Quick status summary')
  .demandCommand(1)
  .help()
  .argv as any;

// ---- EVM bindings (BNB) ----
const BSC_RPC_URL = process.env.BSC_RPC_URL || 'https://bsc-testnet.publicnode.com';
const PROVIDER = new ethers.JsonRpcProvider(BSC_RPC_URL);
const PK = process.env.PRIVATE_KEY;

const ROUTER_ADDRESS = process.env.ROUTER_ADDRESS; // deployed by scripts/deploy.ts
const SLAB_ADDRESS   = process.env.SLAB_ADDRESS;

const RouterAbi = [
  'function admin() view returns (address)',
  'function oracleAuthority() view returns (address)',
  'function riskThresholdBps() view returns (uint16)',
  'function paused() view returns (bool)',
  'function setOracleScore(address asset,uint16 scoreBps)',
  'function mintMandate(address asset,uint8 strategy,uint32 ttlSeconds)',
  'function revokeMandate(address user,address asset,uint8 strategy)',
  'function getMandate(address user,address asset,uint8 strategy) view returns (tuple(address user,address asset,uint8 strategy,uint64 expiresAt,bool exists))'
];

const SlabAbi = [
  'function slabs(address) view returns (bool initialized,uint8 strategy,int64 pnl,uint64 lastSignalTs)',
  'function initializeSlab(uint8 strategy)',
  'function executeSignal(address asset,uint8 strategy,bool isLong,uint16 confidenceBps,int64 notional,int64 price)'
];

function assertEnv(cond: any, msg: string) {
  if (!cond) throw new Error(msg);
}

async function runBNB(cmd: string, args: any) {
  assertEnv(PK, 'PRIVATE_KEY missing');
  assertEnv(ROUTER_ADDRESS, 'ROUTER_ADDRESS missing');
  assertEnv(SLAB_ADDRESS, 'SLAB_ADDRESS missing');

  const wallet = new ethers.Wallet(PK!, PROVIDER);
  const router = new ethers.Contract(ROUTER_ADDRESS!, RouterAbi, wallet);
  const slab   = new ethers.Contract(SLAB_ADDRESS!,   SlabAbi,   wallet);

  if (cmd === 'whoami') {
    console.log('Wallet:', wallet.address);
    console.log('RPC:', BSC_RPC_URL);
    const st = await Promise.all([router.admin(), router.riskThresholdBps(), router.paused()]);
    console.log('Router Admin:', st[0], 'Threshold:', Number(st[1]), 'Paused:', st[2]);
    const acc = await slab.slabs(wallet.address);
    console.log('Slab:', acc);
    return;
  }

  if (cmd === 'oracle-set') {
    const tx = await router.setOracleScore(args.asset, Number(args.score));
    await tx.wait();
    console.log('✅ BNB oracle set', args.asset, args.score);
    return;
  }

  if (cmd === 'mandate-mint') {
    const tx = await router.mintMandate(args.asset, Number(args.strategy), Number(args.ttl ?? 300));
    await tx.wait();
    console.log('✅ BNB mandate minted', args.asset, args.strategy, args.ttl ?? 300);
    return;
  }

  if (cmd === 'deploy') {
    const tx = await slab.initializeSlab(Number(args.strategy));
    await tx.wait();
    console.log('✅ BNB slab initialized', args.strategy);
    return;
  }

  if (cmd === 'execute') {
    const dir = String(args.dir).toLowerCase() === 'long';
    const tx = await slab.executeSignal(
      args.asset,
      Number(args.strategy),
      dir,
      Number(args.conf),
      Number(args.notional),
      Number(args.price)
    );
    await tx.wait();
    console.log('✅ BNB executed', { dir, conf: args.conf, notional: args.notional, price: args.price });
    return;
  }

  if (cmd === 'revoke') {
    const tx = await router.revokeMandate(args.user, args.asset, Number(args.strategy));
    await tx.wait();
    console.log('✅ BNB mandate revoked');
    return;
  }

  if (cmd === 'status') {
    const acc = await slab.slabs(wallet.address);
    console.log('Slab:', acc);
    return;
  }

  throw new Error('Unsupported command on BNB');
}

// ---- Solana route: spawn Rust CLI ----
function runSol(cmd: string, argvList: string[]) {
  // Ensure ./target/release/molly exists → `make cli`
  const out = spawnSync('./target/release/molly', argvList, { stdio: 'inherit' });
  if (out.status !== 0) process.exit(out.status ?? 1);
}

(async () => {
  const [cmd] = argv._;

  if (argv.chain === 'bnb') {
    await runBNB(String(cmd), argv);
    return;
  }

  // Map unified commands to Rust CLI flags for Solana
  const m = new Map<string, string[]>();
  switch (cmd) {
    case 'whoami':
      runSol('whoami', ['whoami']); break;
    case 'init':
      runSol('init', ['init', String(argv.admin), String(argv.oracle), String(argv.threshold ?? 7000)]); break;
    case 'pause':
      runSol('pause', ['pause', String(argv.paused)]); break;
    case 'threshold':
      runSol('threshold', ['threshold', String(argv.bps)]); break;
    case 'oracle-set':
      runSol('oracle-set', ['oracle-set', String(argv.asset), String(argv.score)]); break;
    case 'mandate-mint':
      runSol('mandate-mint', ['mandate-mint', String(argv.asset), String(argv.strategy), String(argv.ttl ?? 300)]); break;
    case 'deploy':
      runSol('deploy', ['deploy', String(argv.strategy)]); break;
    case 'execute':
      runSol('execute', ['execute', String(argv.strategy), String(argv.asset), String(argv.dir), String(argv.conf), String(argv.notional), String(argv.price)]); break;
    case 'revoke':
      runSol('revoke', ['revoke', String(argv.user), String(argv.asset), String(argv.strategy)]); break;
    case 'status':
      runSol('status', ['status']); break;
    default:
      console.error('Unknown command:', cmd);
      process.exit(1);
  }
})().catch((e) => { console.error(e); process.exit(1); });
