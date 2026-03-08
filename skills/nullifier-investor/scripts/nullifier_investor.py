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
            "条件に合う strategy を 3 件見つけました。最上位は BTC Delta Neutral Pool です。",
            "zk proof 済み成績は APY 24.8%、Max DD -6.9%、Sharpe 2.3 です。",
        ]
    )


def verify(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "BTC Delta Neutral Pool の proof は有効です。",
            "APY 24.8%、Max DD -6.9%、Sharpe 2.3 が確認されています。",
        ]
    )


def invest(args: argparse.Namespace) -> str:
    amount = Decimal(str(args.amount)) if args.amount is not None else Decimal("25000")
    asset = args.asset or "USDC"
    return "\n".join(
        [
            f"{format_amount(amount)} {asset} を BTC Delta Neutral Pool に invest しました。",
            "現在評価額は 26,420 USDC、含み益は +1,120 USDC、確定益は 300 USDC です。",
        ]
    )


def position(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "現在評価額は 26,420 USDC です。",
            "含み益は +1,120 USDC、投下元本は 25,000 USDC です。",
        ]
    )


def earnings(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "確定益は 300 USDC です。",
            "引き出し可能な earnings は 1,540 USDC です。",
        ]
    )


def withdraw(args: argparse.Namespace) -> str:
    source = args.source or "earnings"
    amount = Decimal(str(args.amount)) if args.amount is not None else DEFAULT_WITHDRAW_AMOUNT
    if source == "principal":
        return "\n".join(
            [
                f"元本から {format_amount(amount)} USDC の部分 withdraw を受け付けました。",
                "残りのポジション評価額は 26,420 USDC から該当額を差し引いた扱いにしてください。",
            ]
        )

    remaining = max(Decimal("0"), WITHDRAWABLE_EARNINGS - amount)
    return "\n".join(
        [
            f"earnings から {format_amount(amount)} USDC の withdraw を受け付けました。",
            f"残りの引き出し可能額は {format_amount(remaining)} USDC です。",
        ]
    )


def signals(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "最新 signal は BTC/USD buy、price 68,500、confidence 0.85 です。",
            "戦略は引き続き active として配信中です。",
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
