#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { randomUUID } from "node:crypto";

// ---------------------------------------------------------------------------
// Shared data file
// ---------------------------------------------------------------------------
const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_PATH = join(__dirname, "data.json");

function loadData() {
  return JSON.parse(readFileSync(DATA_PATH, "utf-8"));
}

function saveData(data) {
  writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
}

// ---------------------------------------------------------------------------
// Role from env
// ---------------------------------------------------------------------------
const ROLE = process.env.USER_ROLE || "trader"; // "provider" or "trader"

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------
const server = new McpServer({
  name: `zkstrategy-platform-${ROLE}`,
  version: "0.1.0",
});

// ===========================================================================
// Provider tools
// ===========================================================================
if (ROLE === "provider") {
  server.registerTool(
    "strategy_register",
    {
      title: "Register Strategy",
      description: "Register a new trading strategy on the platform",
      inputSchema: {
        name: z.string().describe("Strategy name"),
        description: z.string().optional().describe("Brief description"),
        asset_class: z
          .enum(["crypto", "fx", "us_equity", "real_estate", "prediction_market"])
          .describe("Asset class"),
        apy: z.number().describe("Annual percentage yield"),
        max_drawdown: z.number().describe("Maximum drawdown (e.g. -12)"),
        sharpe_ratio: z.number().describe("Sharpe ratio"),
      },
    },
    async ({ name, description, asset_class, apy, max_drawdown, sharpe_ratio }) => {
      const data = loadData();
      const id = `strat_${randomUUID().slice(0, 8)}`;
      const strategy = {
        id,
        name,
        description: description || "",
        asset_class,
        apy,
        pnl: Math.round(apy * 1000),
        max_drawdown,
        sharpe_ratio,
        proof_status: "unverified",
        proof_data: null,
        provider: process.env.USER_ID || "provider_alice",
        subscribers: 0,
        created_at: new Date().toISOString(),
      };
      data.strategies.push(strategy);
      saveData(data);
      return {
        content: [{ type: "text", text: JSON.stringify(strategy, null, 2) }],
      };
    }
  );

  server.registerTool(
    "strategy_generate_proof",
    {
      title: "Generate zkTLS Proof",
      description: "Generate a zkTLS performance proof for a strategy",
      inputSchema: {
        strategy_id: z.string().describe("Strategy ID"),
      },
    },
    async ({ strategy_id }) => {
      const data = loadData();
      const strategy = data.strategies.find((s) => s.id === strategy_id);
      if (!strategy) {
        return { content: [{ type: "text", text: `Error: strategy ${strategy_id} not found` }] };
      }
      const proof = {
        type: "zktls_v1",
        data_source: "Binance API",
        attested_at: new Date().toISOString(),
        claims: {
          apy: strategy.apy,
          max_drawdown: strategy.max_drawdown,
          sharpe_ratio: strategy.sharpe_ratio,
        },
        proof_hash: `0x${randomUUID().replace(/-/g, "").slice(0, 16)}`,
      };
      strategy.proof_status = "verified";
      strategy.proof_data = proof;
      saveData(data);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              { strategy_id, name: strategy.name, proof, proof_status: "verified" },
              null,
              2
            ),
          },
        ],
      };
    }
  );

  server.registerTool(
    "signal_emit",
    {
      title: "Emit Signal",
      description: "Emit a trading signal to all subscribers of a strategy",
      inputSchema: {
        strategy_id: z.string().describe("Strategy ID"),
        action: z.enum(["BUY", "SELL", "HOLD"]).describe("Trade action"),
        asset: z.string().describe("Asset pair, e.g. BTC/USD"),
        price: z.number().describe("Target price"),
        confidence: z.number().min(0).max(1).optional().describe("Confidence 0.0-1.0"),
        reasoning: z.string().optional().describe("Reasoning for the signal"),
      },
    },
    async ({ strategy_id, action, asset, price, confidence, reasoning }) => {
      const data = loadData();
      const strategy = data.strategies.find((s) => s.id === strategy_id);
      if (!strategy) {
        return { content: [{ type: "text", text: `Error: strategy ${strategy_id} not found` }] };
      }
      const subs = data.subscriptions.filter(
        (s) => s.strategy_id === strategy_id && s.status === "active"
      );
      const signal = {
        signal_id: `sig_${randomUUID().slice(0, 8)}`,
        strategy_id,
        strategy_name: strategy.name,
        timestamp: new Date().toISOString(),
        action,
        asset,
        price,
        confidence: confidence ?? 0.8,
        reasoning: reasoning || "",
        subscribers_notified: subs.length,
      };
      data.signals.push(signal);
      saveData(data);
      return {
        content: [{ type: "text", text: JSON.stringify(signal, null, 2) }],
      };
    }
  );
}

// ===========================================================================
// Trader tools
// ===========================================================================
if (ROLE === "trader") {
  server.registerTool(
    "strategy_search",
    {
      title: "Search Strategies",
      description:
        "Search for trading strategies by performance criteria. Returns all matching strategies with their zkTLS proof status.",
      inputSchema: {
        asset_class: z
          .enum(["crypto", "fx", "us_equity", "real_estate", "prediction_market"])
          .optional()
          .describe("Filter by asset class"),
        min_apy: z.number().optional().describe("Minimum APY percentage"),
        max_drawdown: z.number().optional().describe("Maximum drawdown threshold (e.g. -15)"),
        min_sharpe: z.number().optional().describe("Minimum Sharpe ratio"),
      },
    },
    async ({ asset_class, min_apy, max_drawdown, min_sharpe }) => {
      const data = loadData();
      let results = data.strategies.filter((s) => s.proof_status === "verified");
      if (asset_class) results = results.filter((s) => s.asset_class === asset_class);
      if (min_apy != null) results = results.filter((s) => s.apy >= min_apy);
      if (max_drawdown != null) results = results.filter((s) => s.max_drawdown >= max_drawdown);
      if (min_sharpe != null) results = results.filter((s) => s.sharpe_ratio >= min_sharpe);
      results.sort((a, b) => b.apy - a.apy);
      return {
        content: [{ type: "text", text: JSON.stringify({ strategies: results }, null, 2) }],
      };
    }
  );

  server.registerTool(
    "strategy_verify_proof",
    {
      title: "Verify zkTLS Proof",
      description: "Verify the zkTLS performance proof of a strategy",
      inputSchema: {
        strategy_id: z.string().describe("Strategy ID to verify"),
      },
    },
    async ({ strategy_id }) => {
      const data = loadData();
      const strategy = data.strategies.find((s) => s.id === strategy_id);
      if (!strategy) {
        return { content: [{ type: "text", text: `Error: strategy ${strategy_id} not found` }] };
      }
      if (!strategy.proof_data) {
        return {
          content: [{ type: "text", text: JSON.stringify({ valid: false, reason: "No proof available" }) }],
        };
      }
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                valid: true,
                strategy_id,
                strategy_name: strategy.name,
                proof: strategy.proof_data,
              },
              null,
              2
            ),
          },
        ],
      };
    }
  );

  server.registerTool(
    "strategy_subscribe",
    {
      title: "Subscribe to Strategy",
      description: "Subscribe to a strategy and start receiving trading signals",
      inputSchema: {
        strategy_id: z.string().describe("Strategy ID"),
        allocation: z.number().describe("Amount in USD to allocate"),
      },
    },
    async ({ strategy_id, allocation }) => {
      const data = loadData();
      const strategy = data.strategies.find((s) => s.id === strategy_id);
      if (!strategy) {
        return { content: [{ type: "text", text: `Error: strategy ${strategy_id} not found` }] };
      }
      const sub = {
        id: `sub_${randomUUID().slice(0, 8)}`,
        strategy_id,
        strategy_name: strategy.name,
        trader_id: process.env.USER_ID || "trader_bob",
        allocation,
        status: "active",
        created_at: new Date().toISOString(),
      };
      data.subscriptions.push(sub);
      strategy.subscribers = (strategy.subscribers || 0) + 1;
      saveData(data);
      return {
        content: [{ type: "text", text: JSON.stringify(sub, null, 2) }],
      };
    }
  );

  server.registerTool(
    "signal_get_latest",
    {
      title: "Get Latest Signal",
      description: "Get the latest trading signal from a subscribed strategy",
      inputSchema: {
        strategy_id: z.string().describe("Strategy ID"),
      },
    },
    async ({ strategy_id }) => {
      const data = loadData();
      const signals = data.signals
        .filter((s) => s.strategy_id === strategy_id)
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      if (signals.length === 0) {
        return {
          content: [{ type: "text", text: JSON.stringify({ message: "No signals yet for this strategy" }) }],
        };
      }
      return {
        content: [{ type: "text", text: JSON.stringify(signals[0], null, 2) }],
      };
    }
  );
}

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`zkStrategy MCP Server started (role: ${ROLE})`);
