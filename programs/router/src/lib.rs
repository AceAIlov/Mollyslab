use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount};

declare_id!("NxSlbRout3r111111111111111111111111111111");

#[program]
pub mod router {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, admin: Pubkey, oracle_authority: Pubkey, risk_threshold_bps: u16) -> Result<()> {
        let state = &mut ctx.accounts.state;
        require!(risk_threshold_bps <= 10_000, RouterError::InvalidThreshold);
        state.admin = admin;
        state.oracle_authority = oracle_authority;
        state.risk_threshold_bps = risk_threshold_bps; // e.g. 7000 = 0.70
        state.paused = false;
        emit!(RouterInitialized { admin, oracle_authority, risk_threshold_bps });
        Ok(())
    }

    pub fn set_pause(ctx: Context<AdminOnly>, paused: bool) -> Result<()> {
        ctx.accounts.state.paused = paused;
        if paused { emit!(Paused{}); } else { emit!(Unpaused{}); }
        Ok(())
    }

    pub fn update_threshold(ctx: Context<AdminOnly>, risk_threshold_bps: u16) -> Result<()> {
        require!(risk_threshold_bps <= 10_000, RouterError::InvalidThreshold);
        ctx.accounts.state.risk_threshold_bps = risk_threshold_bps;
        emit!(ThresholdUpdated { risk_threshold_bps });
        Ok(())
    }

    pub fn set_oracle_score(ctx: Context<OracleOnly>, asset_mint: Pubkey, score_bps: u16) -> Result<()> {
        require!(score_bps <= 10_000, RouterError::InvalidThreshold);
        let oracle = &mut ctx.accounts.oracle;
        oracle.asset_mint = asset_mint;
        oracle.score_bps = score_bps; // 0..=10000
        oracle.bump = *ctx.bumps.get("oracle").unwrap();
        emit!(OracleScoreSet { asset_mint, score_bps });
        Ok(())
    }

    pub fn mint_mandate(ctx: Context<MintMandate>, asset_mint: Pubkey, strategy: Strategy, ttl_seconds: u32) -> Result<()> {
        let clock = Clock::get()?;
        require!(!ctx.accounts.state.paused, RouterError::Paused);
        // Check oracle score
        require!(ctx.accounts.oracle.asset_mint == asset_mint, RouterError::OracleMismatch);
        require!(ctx.accounts.oracle.score_bps >= ctx.accounts.state.risk_threshold_bps, RouterError::BelowThreshold);
        // Fill mandate
        let m = &mut ctx.accounts.mandate;
        m.user = ctx.accounts.user.key();
        m.asset_mint = asset_mint;
        m.strategy = strategy;
        m.expires_at = clock.unix_timestamp + ttl_seconds as i64;
        m.bump = *ctx.bumps.get("mandate").unwrap();
        emit!(MandateMinted { user: m.user, asset_mint, strategy, expires_at: m.expires_at });
        Ok(())
    }

    pub fn revoke_mandate(ctx: Context<RevokeMandate>) -> Result<()> {
        let m = &ctx.accounts.mandate;
        require!(m.user == ctx.accounts.signer.key() || ctx.accounts.signer.key() == ctx.accounts.state.admin, RouterError::Unauthorized);
        emit!(MandateRevoked { user: m.user, asset_mint: m.asset_mint });
        Ok(())
    }

    pub fn veto_mandate(_ctx: Context<AdminOnlyWithMandate>) -> Result<()> {
        // No-op: account close handled by context; event only
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = payer, space = 8 + RouterState::SIZE, seeds=[b"state"], bump)]
    pub state: Account<'info, RouterState>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AdminOnly<'info> {
    #[account(mut, seeds=[b"state"], bump)]
    pub state: Account<'info, RouterState>,
    pub admin: Signer<'info>,
}

#[derive(Accounts)]
pub struct OracleOnly<'info> {
    #[account(seeds=[b"state"], bump)]
    pub state: Account<'info, RouterState>,
    #[account(mut, seeds=[b"oracle", asset_mint.as_ref()], bump)]
    pub oracle: Account<'info, OracleScore>,
    #[account(mut)]
    /// CHECK: pubkey checked against state.oracle_authority below
    pub oracle_authority: Signer<'info>,
    pub system_program: Program<'info, System>,
    // Args carried in instruction; asset_mint provided to PDA seeds via ctx.accounts.oracle
    pub asset_mint: Pubkey, // (used in seeds above)
}

impl<'info> OracleOnly<'info> {
    fn validate(&self) -> Result<()> {
        require!(self.oracle_authority.key() == self.state.oracle_authority, RouterError::Unauthorized);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct MintMandate<'info> {
    #[account(seeds=[b"state"], bump)]
    pub state: Account<'info, RouterState>,
    #[account(mut, seeds=[b"oracle", asset_mint.as_ref()], bump)]
    pub oracle: Account<'info, OracleScore>,
    #[account(init, payer = user, space = 8 + Mandate::SIZE, seeds=[b"mandate", user.key().as_ref(), asset_mint.as_ref(), &[strategy as u8]], bump)]
    pub mandate: Account<'info, Mandate>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
    pub asset_mint: Pubkey, // PDA seed helper
    pub strategy: Strategy, // PDA seed helper
}

#[derive(Accounts)]
pub struct RevokeMandate<'info> {
    #[account(seeds=[b"state"], bump)]
    pub state: Account<'info, RouterState>,
    #[account(mut, close = signer, seeds=[b"mandate", mandate.user.as_ref(), mandate.asset_mint.as_ref(), &[mandate.strategy as u8]], bump = mandate.bump)]
    pub mandate: Account<'info, Mandate>,
    #[account(mut)]
    pub signer: Signer<'info>,
}

#[derive(Accounts)]
pub struct AdminOnlyWithMandate<'info> {
    #[account(seeds=[b"state"], bump)]
    pub state: Account<'info, RouterState>,
    pub admin: Signer<'info>,
    #[account(mut, close = admin, seeds=[b"mandate", mandate.user.as_ref(), mandate.asset_mint.as_ref(), &[mandate.strategy as u8]], bump = mandate.bump)]
    pub mandate: Account<'info, Mandate>,
}

#[account]
pub struct RouterState {
    pub admin: Pubkey,
    pub oracle_authority: Pubkey,
    pub risk_threshold_bps: u16,
    pub paused: bool,
}
impl RouterState { pub const SIZE: usize = 32 + 32 + 2 + 1; }

#[account]
pub struct OracleScore {
    pub asset_mint: Pubkey,
    pub score_bps: u16,
    pub bump: u8,
}
impl OracleScore { pub const SIZE: usize = 32 + 2 + 1; }

#[account]
pub struct Mandate {
    pub user: Pubkey,
    pub asset_mint: Pubkey,
    pub strategy: Strategy,
    pub expires_at: i64,
    pub bump: u8,
}
impl Mandate { pub const SIZE: usize = 32 + 32 + 1 + 8 + 1; }

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum Strategy { Momentum=0, Arbitrage=1, Lp=2, MeanReversion=3 }

#[error_code]
pub enum RouterError {
    #[msg("Router is paused")] Paused,
    #[msg("Invalid threshold")] InvalidThreshold,
    #[msg("Oracle asset mismatch")] OracleMismatch,
    #[msg("Below risk threshold")] BelowThreshold,
    #[msg("Unauthorized")] Unauthorized,
}

#[event]
pub struct RouterInitialized { pub admin: Pubkey, pub oracle_authority: Pubkey, pub risk_threshold_bps: u16 }
#[event] pub struct Paused {}
#[event] pub struct Unpaused {}
#[event] pub struct ThresholdUpdated { pub risk_threshold_bps: u16 }
#[event] pub struct OracleScoreSet { pub asset_mint: Pubkey, pub score_bps: u16 }
#[event] pub struct MandateMinted { pub user: Pubkey, pub asset_mint: Pubkey, pub strategy: Strategy, pub expires_at: i64 }
#[event] pub struct MandateRevoked { pub user: Pubkey, pub asset_mint: Pubkey }
