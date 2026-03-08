#!/usr/bin/env python3

from __future__ import annotations

import argparse
from decimal import Decimal


WITHDRAWABLE_REVENUE = Decimal("18240")
DEFAULT_WITHDRAW_AMOUNT = Decimal("10000")


def format_amount(value: Decimal) -> str:
    return f"{value:,.0f}"


def publish(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Published BTC Delta Neutral Pool with proof-backed performance.",
            "Public metrics: APY 24.8%, Max DD -6.9%, Sharpe 2.3.",
        ]
    )


def update(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Updated BTC Delta Neutral Pool.",
            "Latest metrics: APY 24.8%, PnL +412,000 USDC, Max DD -6.9%.",
        ]
    )


def proof_create(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Created a proof for BTC Delta Neutral Pool.",
            "Marked APY 24.8%, Max DD -6.9%, and Sharpe 2.3 as verified.",
        ]
    )


def signal_send(args: argparse.Namespace) -> str:
    action = args.action or "buy"
    asset = args.asset or "BTC/USD"
    price = args.price or "68,500"
    confidence = args.confidence or "0.85"
    return "\n".join(
        [
            "Sent a signal for BTC Delta Neutral Pool.",
            f"Signal payload: {asset} {action} at {price} with confidence {confidence}.",
        ]
    )


def status(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "BTC Delta Neutral Pool is active. Proof status is verified.",
            "Current TVL is 1.84M USDC with 128 investors.",
        ]
    )


def revenue(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Total creator revenue is 42,380 USDC.",
            "Withdrawable revenue is 18,240 USDC.",
        ]
    )


def withdraw(args: argparse.Namespace) -> str:
    amount = Decimal(str(args.amount)) if args.amount is not None else DEFAULT_WITHDRAW_AMOUNT
    remaining = max(Decimal("0"), WITHDRAWABLE_REVENUE - amount)
    return "\n".join(
        [
            f"Accepted a {format_amount(amount)} USDC creator revenue withdrawal.",
            f"Remaining withdrawable balance is {format_amount(remaining)} USDC.",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nullifier creator demo command runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("publish")
    subparsers.add_parser("update")
    subparsers.add_parser("proof-create")

    signal_parser = subparsers.add_parser("signal-send")
    signal_parser.add_argument("--action")
    signal_parser.add_argument("--asset")
    signal_parser.add_argument("--price")
    signal_parser.add_argument("--confidence")

    subparsers.add_parser("status")
    subparsers.add_parser("revenue")

    withdraw_parser = subparsers.add_parser("withdraw")
    withdraw_parser.add_argument("--amount", type=Decimal)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "publish": publish,
        "update": update,
        "proof-create": proof_create,
        "signal-send": signal_send,
        "status": status,
        "revenue": revenue,
        "withdraw": withdraw,
    }
    print(handlers[args.command](args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
