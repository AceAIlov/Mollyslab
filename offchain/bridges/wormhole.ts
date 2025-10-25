/* SPDX-License-Identifier: Apache-2.0
 * NOTE: This is a stub. Wire an actual Wormhole SDK when ready.
 */
import { BridgeAdapter, BridgeReceipt, BridgeTransfer } from "./bridge";

export class WormholeBridge implements BridgeAdapter {
  constructor(private opts: {
    network: "testnet" | "mainnet",
    solRpcUrl?: string,
    bnbRpcUrl?: string,
    // guardianRpc?: string,
    // coreBridgeIds?: { sol: string; bnb: string; }
    // tokenBridgeIds?: { sol: string; bnb: string; }
  }) {}

  async transferAndCall(req: BridgeTransfer): Promise<BridgeReceipt> {
    // TODO: Implement with Wormhole token bridge + (optional) payload
    // Pseudocode:
    //  - if req.fromChain === "sol": build & sign Anchor CPI to token bridge
    //  - if req.fromChain === "bnb": build & sign ERC20 approve/transfer to token bridge
    //  - publish message, receive sequence
    //  - return { status: "submitted", txHash, vaaId? }
    return { requestId: mkId(), status: "failed", error: "Wormhole not wired yet" };
  }

  async waitForFinality(receipt: BridgeReceipt): Promise<BridgeReceipt> {
    // TODO: Poll guardians / RPC to confirm VAA + redemption
    return { ...receipt, status: "failed", error: "waitForFinality not implemented" };
  }
}

function mkId(): string {
  return Math.random().toString(36).slice(2);
}
