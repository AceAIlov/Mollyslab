/* SPDX-License-Identifier: Apache-2.0
 * Copyright (c) 2025 MollySlab Contributors
 */
import { randomBytes } from "crypto";

export type Chain = "sol" | "bnb";

export type BridgeTransfer = {
  fromChain: Chain;           // "sol" | "bnb"
  toChain: Chain;             // "sol" | "bnb"
  token: string;              // mint (Sol) or ERC20 (BNB)
  amount: bigint;             // atomic units
  sender: string;             // base58 on Sol, 0x.. on BNB
  recipient: string;          // destination wallet
  // Optional payload to trigger an action on arrival (e.g., trade on destination slab)
  // Keep it small; encode as UTF-8 JSON string.
  memoJson?: string;
};

export type BridgeReceipt = {
  requestId: string;          // client-assigned or generated
  txHash?: string;            // source-chain tx
  vaaId?: string;             // bridge message id (if applicable)
  status: "submitted" | "finalized" | "failed";
  error?: string;
};

export interface BridgeAdapter {
  /**
   * Move tokens from source to destination chain and optionally include a small memo payload.
   * Should return after submit; callers can poll `waitForFinality` or their own indexer.
   */
  transferAndCall(req: BridgeTransfer): Promise<BridgeReceipt>;

  /**
   * Block/poll until bridge finality (best effort).
   * For mock, we finalize instantly. Real adapters should poll provider/RPC/guardians.
   */
  waitForFinality(receipt: BridgeReceipt, timeoutMs?: number): Promise<BridgeReceipt>;
}

/**
 * Mock bridge (dev/test): no real chain calls. It "finalizes" immediately and echoes a synthetic txHash.
 * Useful for localnet & CI, and for unit tests of cross-chain orchestration.
 */
export class MockBridge implements BridgeAdapter {
  async transferAndCall(req: BridgeTransfer): Promise<BridgeReceipt> {
    // Basic sanity checks
    if (req.fromChain === req.toChain) {
      return { requestId: genId(), status: "failed", error: "fromChain equals toChain" };
    }
    if (req.amount <= 0n) {
      return { requestId: genId(), status: "failed", error: "amount must be > 0" };
    }

    const rid = genId();
    // In a real adapter, submit a tx here and return "submitted" + tx hash.
    const txHash = "0x" + Buffer.from(randomBytes(32)).toString("hex");
    console.info(`[MockBridge] ${req.fromChain} → ${req.toChain} ${req.amount} ${req.token} to ${req.recipient} memo=${req.memoJson ?? "<none>"} tx=${txHash}`);
    return { requestId: rid, txHash, status: "submitted" };
  }

  async waitForFinality(receipt: BridgeReceipt): Promise<BridgeReceipt> {
    // Pretend it finalized; real adapters should poll.
    return { ...receipt, status: "finalized", vaaId: receipt.vaaId ?? genId() };
  }
}

function genId(): string {
  return Buffer.from(randomBytes(12)).toString("hex");
}
