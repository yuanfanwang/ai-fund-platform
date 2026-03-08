#!/usr/bin/env python3

from __future__ import annotations

import argparse
from decimal import Decimal


WITHDRAWABLE_EARNINGS = Decimal("1540")
DEFAULT_WITHDRAW_AMOUNT = Decimal("1000")


def format_amount(value: Decimal) -> str:
    return f"{value:,.0f}"


def explore(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Found 3 matching strategies. The top result is BTC Delta Neutral Pool.",
            "Verified metrics: APY 24.8%, Max DD -6.9%, Sharpe 2.3.",
        ]
    )


def verify(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "The proof for BTC Delta Neutral Pool is valid.",
            "Confirmed APY 24.8%, Max DD -6.9%, and Sharpe 2.3.",
        ]
    )


def invest(args: argparse.Namespace) -> str:
    amount = Decimal(str(args.amount)) if args.amount is not None else Decimal("25000")
    asset = args.asset or "USDC"
    return "\n".join(
        [
            f"Invested {format_amount(amount)} {asset} into BTC Delta Neutral Pool.",
            "Current value is 26,420 USDC, unrealized PnL is +1,120 USDC, and realized earnings are 300 USDC.",
        ]
    )


def position(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Current value is 26,420 USDC.",
            "Unrealized PnL is +1,120 USDC and invested principal is 25,000 USDC.",
        ]
    )


def earnings(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Realized earnings are 300 USDC.",
            "Withdrawable earnings are 1,540 USDC.",
        ]
    )


def withdraw(args: argparse.Namespace) -> str:
    source = args.source or "earnings"
    amount = Decimal(str(args.amount)) if args.amount is not None else DEFAULT_WITHDRAW_AMOUNT
    if source == "principal":
        return "\n".join(
            [
                f"Accepted a {format_amount(amount)} USDC principal withdrawal.",
                "Treat the remaining position value as 26,420 USDC minus the withdrawn amount.",
            ]
        )

    remaining = max(Decimal("0"), WITHDRAWABLE_EARNINGS - amount)
    return "\n".join(
        [
            f"Accepted a {format_amount(amount)} USDC earnings withdrawal.",
            f"Remaining withdrawable earnings are {format_amount(remaining)} USDC.",
        ]
    )


def signals(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "Latest signal: BTC/USD buy at 68,500 with confidence 0.85.",
            "The strategy remains active and is still broadcasting signals.",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nullifier investor demo command runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    explore_parser = subparsers.add_parser("explore")
    explore_parser.add_argument("--asset-class")
    explore_parser.add_argument("--min-apy")
    explore_parser.add_argument("--max-drawdown")
    explore_parser.add_argument("--min-sharpe")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--strategy-id")

    invest_parser = subparsers.add_parser("invest")
    invest_parser.add_argument("--strategy-id")
    invest_parser.add_argument("--amount", type=Decimal)
    invest_parser.add_argument("--asset")

    subparsers.add_parser("position")
    subparsers.add_parser("earnings")

    withdraw_parser = subparsers.add_parser("withdraw")
    withdraw_parser.add_argument("--amount", type=Decimal)
    withdraw_parser.add_argument("--source", choices=("earnings", "principal"))

    subparsers.add_parser("signals")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "explore": explore,
        "verify": verify,
        "invest": invest,
        "position": position,
        "earnings": earnings,
        "withdraw": withdraw,
        "signals": signals,
    }
    print(handlers[args.command](args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
