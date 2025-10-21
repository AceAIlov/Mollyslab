import * as anchor from '@coral-xyz/anchor';
import { Program } from '@coral-xyz/anchor';
import { Keypair, PublicKey } from '@solana/web3.js';
import { expect } from 'chai';

describe('admin controls — pause, threshold, fail on below-threshold', () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const wallet = (provider.wallet as any).payer as Keypair;

  const routerId = new PublicKey('NxSlbRout3r111111111111111111111111111111');
  // @ts-ignore
  const router = new Program(JSON.parse(require('fs').readFileSync('./target/idl/router.json','utf8')), routerId, provider);

  it('pause/unpause + update threshold', async () => {
    const [state] = PublicKey.findProgramAddressSync([Buffer.from('state')], routerId);
    await router.methods.initialize(wallet.publicKey, wallet.publicKey, 7000)
      .accounts({ state, payer: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId })
      .rpc();

    await router.methods.setPause(true)
      .accounts({ state, admin: wallet.publicKey })
      .rpc();
    const st: any = await router.account.routerState.fetch(state);
    expect(st.paused).to.eq(true);

    await router.methods.setPause(false)
      .accounts({ state, admin: wallet.publicKey })
      .rpc();
    const st2: any = await router.account.routerState.fetch(state);
    expect(st2.paused).to.eq(false);

    await router.methods.updateThreshold(8000)
      .accounts({ state, admin: wallet.publicKey })
      .rpc();
    const st3: any = await router.account.routerState.fetch(state);
    expect(st3.riskThresholdBps).to.eq(8000);
  });

  it('below-threshold mandate mint should fail', async () => {
    const [state] = PublicKey.findProgramAddressSync([Buffer.from('state')], routerId);
    const assetMint = Keypair.generate().publicKey;
    const [oracle] = PublicKey.findProgramAddressSync([Buffer.from('oracle'), assetMint.toBuffer()], routerId);

    await router.methods.setOracleScore(assetMint, 6000)
      .accounts({ state, oracle, oracleAuthority: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId, assetMint })
      .rpc();

    const strat = { momentum: {} } as any;
    const [mandate] = PublicKey.findProgramAddressSync([Buffer.from('mandate'), wallet.publicKey.toBuffer(), assetMint.toBuffer(), Buffer.from([0])], routerId);

    let failed = false;
    try {
      await router.methods.mintMandate(assetMint, strat, 300)
        .accounts({ state, oracle, mandate, user: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId, assetMint, strategy: strat })
        .rpc();
    } catch (e) { failed = true; }
    expect(failed).to.eq(true);
  });
});
