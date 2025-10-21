import * as anchor from '@coral-xyz/anchor';
import { Program } from '@coral-xyz/anchor';
import { Keypair, PublicKey } from '@solana/web3.js';
import { expect } from 'chai';

describe('slab edge cases — low confidence & expiry', () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const wallet = (provider.wallet as any).payer as Keypair;

  const routerId = new PublicKey('NxSlbRout3r111111111111111111111111111111');
  const slabId = new PublicKey('NxSlabExec1111111111111111111111111111111');
  // @ts-ignore
  const router = new Program(JSON.parse(require('fs').readFileSync('./target/idl/router.json','utf8')), routerId, provider);
  // @ts-ignore
  const slab = new Program(JSON.parse(require('fs').readFileSync('./target/idl/slab.json','utf8')), slabId, provider);

  it('low confidence should fail; then expiry should fail', async () => {
    const [state] = PublicKey.findProgramAddressSync([Buffer.from('state')], routerId);
    await router.methods.initialize(wallet.publicKey, wallet.publicKey, 7000)
      .accounts({ state, payer: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId })
      .rpc();

    const assetMint = Keypair.generate().publicKey;
    const [oracle] = PublicKey.findProgramAddressSync([Buffer.from('oracle'), assetMint.toBuffer()], routerId);
    await router.methods.setOracleScore(assetMint, 9000)
      .accounts({ state, oracle, oracleAuthority: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId, assetMint })
      .rpc();

    const strat = { momentum: {} } as any;
    const [mandate] = PublicKey.findProgramAddressSync([Buffer.from('mandate'), wallet.publicKey.toBuffer(), assetMint.toBuffer(), Buffer.from([0])], routerId);
    await router.methods.mintMandate(assetMint, strat, 1)
      .accounts({ state, oracle, mandate, user: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId, assetMint, strategy: strat })
      .rpc();

    const [slabPda] = PublicKey.findProgramAddressSync([Buffer.from('slab'), wallet.publicKey.toBuffer()], slabId);
    await slab.methods.initializeSlab(strat)
      .accounts({ slab: slabPda, user: wallet.publicKey, systemProgram: anchor.web3.SystemProgram.programId })
      .rpc();

    // Low confidence
    let low = false;
    try {
      await slab.methods.executeSignal(8000, { long: {} }, new anchor.BN(1000), new anchor.BN(100))
        .accounts({ slab: slabPda, mandate })
        .rpc();
    } catch (e) { low = true; }
    expect(low).to.eq(true);

    await new Promise((r) => setTimeout(r, 1100));

    let expired = false;
    try {
      await slab.methods.executeSignal(9000, { long: {} }, new anchor.BN(1000), new anchor.BN(100))
        .accounts({ slab: slabPda, mandate })
        .rpc();
    } catch (e) { expired = true; }
    expect(expired).to.eq(true);
  });
});
