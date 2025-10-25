/* SPDX-License-Identifier: Apache-2.0 */
import { BridgeAdapter, MockBridge } from "./bridge";
import { WormholeBridge } from "./wormhole";

export function createBridge(): BridgeAdapter {
  const impl = (process.env.BRIDGE_IMPL || "mock").toLowerCase();
  if (impl === "wormhole") {
    return new WormholeBridge({
      network: (process.env.WH_NETWORK as any) || "testnet",
      solRpcUrl: process.env.RPC_URL || "http://127.0.0.1:8899",
      bnbRpcUrl: process.env.BSC_RPC_URL || "https://bsc-testnet.publicnode.com",
    });
  }
  return new MockBridge();
}
