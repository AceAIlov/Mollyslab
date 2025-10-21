use anchor_lang::prelude::*;

declare_id!("NxSlabExec1111111111111111111111111111111");

#[program]
pub mod slab {
    use super::*;

    pub fn initialize_slab(ctx: Context<InitializeSlab>, strategy: Strategy) -> Result<()> {
        let s = &mut ctx.accounts.slab;
        s.owner = ctx.accounts.user.key();
        s.strategy = strategy;
        s.performance_pnl = 0;
        s.last_signal_ts = 0;
        s.bump = *ctx.bumps.get("slab").unwrap();
        emit!(SlabInitialized { owner: s.owner, strategy });
        Ok(())
    }

    pub fn execute_signal(ctx: Context<ExecuteSignal>, confidence_bps: u16, direction: Side, notional: i64, price: i64) -> Result<()> {
        let clock = Clock::get()?;
        require!(confidence_bps <= 10_000, SlabError::Invalid);
        require!(confidence_bps >= 8_500, SlabError::LowConfidence); // 85%
        require!(clock.unix_timestamp <= ctx.accounts.mandate.expires_at, SlabError::MandateExpired);

        let s = &mut ctx.accounts.slab;
        let pnl_delta = match direction { Side::Long => notional, Side::Short => -notional };
        s.performance_pnl = s.performance_pnl.saturating_add(pnl_delta);
        s.last_signal_ts = clock.unix_timestamp;
        emit!(SignalExecuted { owner: s.owner, strategy: s.strategy, direction, confidence_bps, notional, price, pnl_after: s.performance_pnl });
        Ok(())
    }

    pub fn close_slab(_ctx: Context<CloseSlab>) -> Result<()> {
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeSlab<'info> {
    #[account(init, payer = user, space = 8 + SlabAccount::SIZE, seeds=[b"slab", user.key().as_ref()], bump)]
    pub slab: Account<'info, SlabAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecuteSignal<'info> {
    #[account(mut, seeds=[b"slab", slab.owner.as_ref()], bump = slab.bump)]
    pub slab: Account<'info, SlabAccount>,
    /// CHECK: mirror router::Mandate PDA
    #[account(seeds=[b"mandate", mandate.user.as_ref(), mandate.asset_mint.as_ref(), &[mandate.strategy as u8]], bump = mandate.bump)]
    pub mandate: Account<'info, MandateMirror>,
}

#[derive(Accounts)]
pub struct CloseSlab<'info> {
    #[account(mut, close = user, seeds=[b"slab", slab.owner.as_ref()], bump = slab.bump)]
    pub slab: Account<'info, SlabAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
}

#[account]
pub struct SlabAccount {
    pub owner: Pubkey,
    pub strategy: Strategy,
    pub performance_pnl: i64,
    pub last_signal_ts: i64,
    pub bump: u8,
}
impl SlabAccount { pub const SIZE: usize = 32 + 1 + 8 + 8 + 1; }

#[account]
#[derive(Default)]
pub struct MandateMirror {
    pub user: Pubkey,
    pub asset_mint: Pubkey,
    pub strategy: Strategy,
    pub expires_at: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum Strategy { Momentum=0, Arbitrage=1, Lp=2, MeanReversion=3 }

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum Side { Long=0, Short=1 }

#[event] pub struct SlabInitialized { pub owner: Pubkey, pub strategy: Strategy }
#[event] pub struct SignalExecuted { pub owner: Pubkey, pub strategy: Strategy, pub direction: Side, pub confidence_bps: u16, pub notional: i64, pub price: i64, pub pnl_after: i64 }

#[error_code]
pub enum SlabError {
    #[msg("Invalid input")] Invalid,
    #[msg("Confidence below 85% threshold")] LowConfidence,
    #[msg("Mandate expired")] MandateExpired,
}
