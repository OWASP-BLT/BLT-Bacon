"""
BLT-BACON Token Distribution Service
A Cloudflare Python Worker for distributing BACON tokens on Bitcoin using Runes protocol.
"""

import json
import os
import subprocess
from typing import Any, Dict, List

import yaml


class Response:
    """Simple response class for Cloudflare Workers."""

    def __init__(self, body: str, status: int = 200, headers: Dict[str, str] = None):
        self.body = body
        self.status = status
        self.headers = headers or {"Content-Type": "application/json"}


class BaconWorker:
    """Main worker class for BACON token distribution."""

    def __init__(self):
        self.ord_path = os.getenv("ORD_PATH", "/usr/local/bin/ord")
        self.yaml_file_path = os.getenv("YAML_FILE_PATH", "/tmp/batch.yaml")

        # Bitcoin RPC Configuration for Mainnet
        self.bitcoin_rpc_user_mainnet = os.getenv("BITCOIN_RPC_USER_MAINNET", "bitcoin_mainnet")
        self.bitcoin_rpc_password_mainnet = os.getenv("BITCOIN_RPC_PASSWORD_MAINNET", "password_mainnet")
        self.bitcoin_rpc_url_mainnet = os.getenv("BITCOIN_RPC_URL_MAINNET", "http://bitcoin-node-ip:8332")
        self.bitcoin_datadir_mainnet = os.getenv("BITCOIN_DATADIR_MAINNET", "/blockchain/bitcoin/data")

        # Bitcoin RPC Configuration for Regtest
        self.bitcoin_rpc_user_regtest = os.getenv("BITCOIN_RPC_USER_REGTEST", "bitcoin_regtest")
        self.bitcoin_rpc_password_regtest = os.getenv("BITCOIN_RPC_PASSWORD_REGTEST", "password_regtest")
        self.bitcoin_rpc_url_regtest = os.getenv("BITCOIN_RPC_URL_REGTEST", "http://regtest-node-ip:18443")
        self.bitcoin_datadir_regtest = os.getenv("BITCOIN_DATADIR_REGTEST", "/blockchain/regtest/data")

        # Ordinal Server Configuration
        self.ord_server_url_mainnet = os.getenv("ORD_SERVER_URL_MAINNET", "http://ord-server-ip:9001")
        self.ord_server_url_regtest = os.getenv("ORD_SERVER_URL_REGTEST", "http://regtest-server-ip:9001")

        # Wallet Configuration
        self.wallet_name_mainnet = os.getenv("WALLET_NAME_MAINNET", "master-wallet")
        self.wallet_name_regtest = os.getenv("WALLET_NAME_REGTEST", "regtest-wallet")
        self.wallet_address_regtest = os.getenv("WALLET_ADDRESS_REGTEST", "bcrt1")
        self.wallet_api_password = os.getenv("WALLET_API_PASSWORD", "wallet_password")

    def send_bacon_tokens_mainnet(self, request_data: Dict[str, Any]) -> Response:
        """Send BACON tokens on mainnet."""
        yaml_content = request_data.get("yaml_content")
        fee_rate = request_data.get("fee_rate")
        is_dry_run = request_data.get("dry_run", True)

        if not yaml_content:
            return Response(
                json.dumps({"success": False, "error": "YAML content missing"}),
                status=400,
            )

        if not fee_rate or not isinstance(fee_rate, (int, float)):
            return Response(
                json.dumps({"success": False, "error": "Valid fee_rate is required"}),
                status=400,
            )

        if not is_dry_run:
            password = request_data.get("password")
            if not password:
                return Response(
                    json.dumps({"success": False, "error": "Password is required for non-dry-run transactions"}),
                    status=400,
                )
            elif password != self.wallet_api_password:
                return Response(
                    json.dumps({"success": False, "error": "Invalid password"}),
                    status=401,
                )

        # Write YAML to a temporary file
        with open(self.yaml_file_path, "w") as file:
            file.write(yaml_content)

        command = [
            "sudo",
            self.ord_path,
            f"--bitcoin-rpc-username={self.bitcoin_rpc_user_mainnet}",
            f"--bitcoin-rpc-password={self.bitcoin_rpc_password_mainnet}",
            f"--bitcoin-rpc-url={self.bitcoin_rpc_url_mainnet}",
            "wallet",
            f"--server-url={self.ord_server_url_mainnet}",
            f"--name={self.wallet_name_mainnet}",
            "split",
            f"--splits={self.yaml_file_path}",
            f"--fee-rate={fee_rate}",
        ]

        if is_dry_run:
            command.append("--dry-run")

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            txid = result.stdout.strip()
            return Response(
                json.dumps({
                    "success": True,
                    "txid": txid,
                    "dry_run": is_dry_run,
                }),
                status=200,
            )
        except subprocess.CalledProcessError as e:
            return Response(
                json.dumps({
                    "success": False,
                    "error": e.stderr,
                    "dry_run": is_dry_run,
                }),
                status=500,
            )

    def send_bacon_tokens_regtest(self, request_data: Dict[str, Any]) -> Response:
        """Send BACON tokens on regtest."""
        num_users = request_data.get("num_users")
        fee_rate = request_data.get("fee_rate")

        if not num_users or not isinstance(num_users, int) or num_users <= 0:
            return Response(
                json.dumps({"success": False, "error": "num_users must be a positive integer"}),
                status=400,
            )

        if not fee_rate or not isinstance(fee_rate, (int, float)):
            return Response(
                json.dumps({"success": False, "error": "Valid fee_rate is required"}),
                status=400,
            )

        # Generate YAML batch transaction file
        yaml_data = {
            "outputs": [
                {
                    "address": self.wallet_address_regtest,
                    "runes": {"BLT•BACON•TOKENS": 1},
                }
                for _ in range(num_users)
            ]
        }

        with open(self.yaml_file_path, "w") as file:
            yaml.dump(yaml_data, file, default_flow_style=False)

        # Run the transaction split command
        command = [
            "sudo",
            self.ord_path,
            f"--bitcoin-rpc-username={self.bitcoin_rpc_user_regtest}",
            f"--bitcoin-rpc-password={self.bitcoin_rpc_password_regtest}",
            f"--bitcoin-rpc-url={self.bitcoin_rpc_url_regtest}",
            "-r",
            "wallet",
            f"--server-url={self.ord_server_url_regtest}",
            f"--name={self.wallet_name_regtest}",
            "split",
            f"--splits={self.yaml_file_path}",
            f"--fee-rate={fee_rate}",
            "--dry-run",
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            txid = result.stdout.strip()
            return Response(
                json.dumps({"success": True, "txid": txid, "dry_run": True}),
                status=200,
            )
        except subprocess.CalledProcessError as e:
            return Response(
                json.dumps({"success": False, "error": e.stderr, "dry_run": True}),
                status=500,
            )

    def get_wallet_balance_mainnet(self) -> Response:
        """Get wallet balance on mainnet."""
        command = [
            "sudo",
            self.ord_path,
            f"--bitcoin-rpc-username={self.bitcoin_rpc_user_mainnet}",
            f"--bitcoin-rpc-password={self.bitcoin_rpc_password_mainnet}",
            f"--bitcoin-rpc-url={self.bitcoin_rpc_url_mainnet}",
            f"--data-dir={self.bitcoin_datadir_mainnet}",
            "wallet",
            f"--server-url={self.ord_server_url_mainnet}",
            f"--name={self.wallet_name_mainnet}",
            "balance",
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            balance_output = result.stdout.strip()
            return Response(
                json.dumps({
                    "success": True,
                    "balance": balance_output,
                }),
                status=200,
            )
        except subprocess.CalledProcessError as e:
            return Response(
                json.dumps({
                    "success": False,
                    "error": e.stderr,
                }),
                status=500,
            )

    async def handle_request(self, request: Any) -> Response:
        """Main request handler."""
        try:
            # Parse URL path
            url = request.url
            path = url.split("://")[1].split("/", 1)[1] if "/" in url.split("://")[1] else ""

            # Handle different endpoints
            if path == "mainnet/send-bacon-tokens" and request.method == "POST":
                body = await request.json()
                return self.send_bacon_tokens_mainnet(body)

            elif path == "regtest/send-bacon-tokens" and request.method == "POST":
                body = await request.json()
                return self.send_bacon_tokens_regtest(body)

            elif path == "mainnet/wallet-balance" and request.method == "GET":
                return self.get_wallet_balance_mainnet()

            elif path == "" or path == "/" or path == "health":
                return Response(
                    json.dumps({
                        "status": "healthy",
                        "service": "BLT-BACON Token Distribution Service",
                        "version": "1.0.0",
                    }),
                    status=200,
                )

            else:
                return Response(
                    json.dumps({"error": "Not found"}),
                    status=404,
                )

        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
            )


# Cloudflare Worker entry point
try:
    from workers import WorkerEntrypoint

    class Default(WorkerEntrypoint):
        async def fetch(self, request):
            worker = BaconWorker()
            return await worker.handle_request(request)

except ImportError:
    # Fallback for local testing without Cloudflare Workers SDK
    worker = BaconWorker()
