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
            "BTC Delta Neutral Pool を publish しました。zk proof 付き成績を公開済みです。",
            "公開メトリクスは APY 24.8%、Max DD -6.9%、Sharpe 2.3 です。",
        ]
    )


def update(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "BTC Delta Neutral Pool を update しました。",
            "最新メトリクスは APY 24.8%、PnL +412,000 USDC、Max DD -6.9% です。",
        ]
    )


def proof_create(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "BTC Delta Neutral Pool の proof を作成しました。",
            "APY 24.8%、Max DD -6.9%、Sharpe 2.3 を証明済みとして更新しました。",
        ]
    )


def signal_send(args: argparse.Namespace) -> str:
    action = args.action or "buy"
    asset = args.asset or "BTC/USD"
    price = args.price or "68,500"
    confidence = args.confidence or "0.85"
    return "\n".join(
        [
            "BTC Delta Neutral Pool の signal を送信しました。",
            f"配信内容は {asset} {action}、price {price}、confidence {confidence} として扱います。",
        ]
    )


def status(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "BTC Delta Neutral Pool は active です。proof status は verified です。",
            "現在の TVL は 1.84M USDC、investor 数は 128 です。",
        ]
    )


def revenue(_: argparse.Namespace) -> str:
    return "\n".join(
        [
            "累計 revenue は 42,380 USDC です。",
            "withdraw 可能額は 18,240 USDC です。",
        ]
    )


def withdraw(args: argparse.Namespace) -> str:
    amount = Decimal(str(args.amount)) if args.amount is not None else DEFAULT_WITHDRAW_AMOUNT
    remaining = max(Decimal("0"), WITHDRAWABLE_REVENUE - amount)
    return "\n".join(
        [
            f"creator revenue から {format_amount(amount)} USDC の withdraw を受け付けました。",
            f"withdraw 可能残高は {format_amount(remaining)} USDC です。",
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
