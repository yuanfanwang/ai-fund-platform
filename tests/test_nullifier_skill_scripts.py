import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CREATOR_SCRIPT = REPO_ROOT / "skills" / "nullifier-creator" / "scripts" / "nullifier_creator.py"
INVESTOR_SCRIPT = REPO_ROOT / "skills" / "nullifier-investor" / "scripts" / "nullifier_investor.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


class NullifierCreatorScriptTests(unittest.TestCase):
    def test_publish_returns_canonical_demo_copy(self) -> None:
        result = run_script(CREATOR_SCRIPT, "publish")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Published BTC Delta Neutral Pool with proof-backed performance.",
                    "Public metrics: APY 24.8%, Max DD -6.9%, Sharpe 2.3.",
                ]
            ),
        )

    def test_status_returns_canonical_tvl_and_investor_count(self) -> None:
        result = run_script(CREATOR_SCRIPT, "status")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "BTC Delta Neutral Pool is active. Proof status is verified.",
                    "Current TVL is 1.84M USDC with 128 investors.",
                ]
            ),
        )

    def test_revenue_returns_canonical_balances(self) -> None:
        result = run_script(CREATOR_SCRIPT, "revenue")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Total creator revenue is 42,380 USDC.",
                    "Withdrawable revenue is 18,240 USDC.",
                ]
            ),
        )

    def test_withdraw_defaults_to_ten_thousand(self) -> None:
        result = run_script(CREATOR_SCRIPT, "withdraw")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Accepted a 10,000 USDC creator revenue withdrawal.",
                    "Remaining withdrawable balance is 8,240 USDC.",
                ]
            ),
        )


class NullifierInvestorScriptTests(unittest.TestCase):
    def test_explore_returns_canonical_top_strategy(self) -> None:
        result = run_script(
            INVESTOR_SCRIPT,
            "explore",
            "--asset-class",
            "crypto",
            "--min-apy",
            "20",
            "--max-drawdown",
            "10",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Found 3 matching strategies. The top result is BTC Delta Neutral Pool.",
                    "Verified metrics: APY 24.8%, Max DD -6.9%, Sharpe 2.3.",
                ]
            ),
        )

    def test_invest_returns_canonical_position_summary(self) -> None:
        result = run_script(
            INVESTOR_SCRIPT,
            "invest",
            "--strategy-id",
            "strat_btc_delta_neutral",
            "--amount",
            "25000",
            "--asset",
            "USDC",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Invested 25,000 USDC into BTC Delta Neutral Pool.",
                    "Current value is 26,420 USDC, unrealized PnL is +1,120 USDC, and realized earnings are 300 USDC.",
                ]
            ),
        )

    def test_withdraw_defaults_to_one_thousand_from_earnings(self) -> None:
        result = run_script(INVESTOR_SCRIPT, "withdraw")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Accepted a 1,000 USDC earnings withdrawal.",
                    "Remaining withdrawable earnings are 540 USDC.",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
