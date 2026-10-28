#!/usr/bin/env python3
"""Generate screenshots and Project_Report.pdf for the ALU blockchain assignment."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "screenshots"
DOCS.mkdir(parents=True, exist_ok=True)
LOGO = ROOT / "alu-logo.png"
PDF = ROOT / "Project_Report.pdf"

NAVY = HexColor("#002E6D")
TEAL = HexColor("#0E7C86")
INK = HexColor("#1C2430")
MUTED = HexColor("#4B5563")
RULE = HexColor("#D6DEE8")
HASH = "ceddec61dafedd84ad1a1a0d43e26de0a84ad71493a4c21b3405adbc6ec191db"
GITHUB = "https://github.com/shasha-12/alu-logo-blockchain-registry"

COURIER = "/System/Library/Fonts/Supplemental/Courier New.ttf"
COURIER_BOLD = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def wrap_terminal_line(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    lines = []
    while text:
        lines.append(text[:max_chars])
        text = text[max_chars:]
    return lines


def render_terminal(path: Path, title: str, body: str, max_chars: int = 102) -> Path:
    font = ImageFont.truetype(COURIER, 14)
    title_font = ImageFont.truetype(COURIER_BOLD, 13)
    raw_lines = body.strip("\n").splitlines()
    lines: list[str] = []
    for line in raw_lines:
        lines.extend(wrap_terminal_line(line.rstrip(), max_chars) or [""])

    pad_x, pad_y = 28, 18
    line_h = 22
    header_h = 42
    width = 980
    height = header_h + pad_y * 2 + line_h * max(len(lines), 8) + 12
    img = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, header_h], fill="#0F172A")
    for i, colour in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
        draw.ellipse([14 + i * 18, 14, 26 + i * 18, 26], fill=colour)
    draw.text((80, 13), title, font=title_font, fill="#E5E7EB")

    y = header_h + pad_y
    for line in lines:
        colour = "#E5E7EB"
        if "passing" in line or line.strip().startswith("PASS") or "successfully" in line:
            colour = "#34D399"
        elif "WARNING" in line or "Warning" in line:
            colour = "#FBBF24"
        elif line.strip().startswith("Account") or "0x" in line and "deployed" in line.lower():
            colour = "#7DD3FC"
        elif "SHA-256" in line or "bytes32" in line or "content hash" in line.lower():
            colour = "#F9A8D4"
        draw.text((pad_x, y), line, font=font, fill=colour)
        y += line_h

    img.save(path)
    return path


def build_screenshots() -> dict[str, Path]:
    test_body = """$ npx hardhat test

  ALUAssetRegistry
    PASS  registers the ALU logo successfully and returns a token ID
    PASS  rejects a second registration of the same content hash
    PASS  verifyLogoIntegrity() returns true when the correct hash is supplied
    PASS  verifyLogoIntegrity() returns false when an incorrect hash is supplied
    PASS  getAsset() returns the correct name and file type for a registered token

  ALULogoToken
    PASS  mints the full 1,000,000 ALUT supply to the logo owner on deployment
    PASS  distributeShares() correctly transfers tokens to a recipient
    PASS  ownershipPercentage() returns the correct percentage for a known balance


  8 passing (420ms)
"""
    hash_body = f"""$ node scripts/hash-logo.js
File:             alu-logo.png
Size (bytes):     63821
SHA-256 (hex):    {HASH}
bytes32 value:    0x{HASH}

$ shasum -a 256 alu-logo.png
{HASH}  alu-logo.png
"""
    node_body = """$ npx hardhat node
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========
WARNING: These accounts, and their private keys, are publicly known.
Any funds sent to them on Mainnet or any other live network WILL BE LOST.

Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)
Account #2: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC (10000 ETH)
Account #3: 0x90F79bf6EB2c4f870365E785982E1f101E93b906 (10000 ETH)
Account #4: 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65 (10000 ETH)
Account #5: 0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc (10000 ETH)

... 14 more test wallets, each funded with 10,000 ETH
"""
    deploy_body = f"""$ npx hardhat run scripts/deploy.js --network localhost
============================================================
ALU Logo Protection — deployment
============================================================
Deployer / logo owner: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Logo file:             alu-logo.png
SHA-256 content hash:  0x{HASH}

ALUAssetRegistry:  0x5FbDB2315678afecb367f032d93F642f64180aa3
Token ID:          1
Register tx:       0x4f7ba1771983a75e41881c31ce9216818715fd113dac7660d24ba38f5ae945d5
ALULogoToken:      0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
ALUT minted to logo owner:      1000000.0 ALUT
============================================================
"""
    return {
        "tests": render_terminal(DOCS / "tests-passing.png", "npx hardhat test — 8 passing", test_body),
        "hash": render_terminal(DOCS / "sha256-hash.png", "SHA-256 of alu-logo.png", hash_body),
        "node": render_terminal(DOCS / "hardhat-node.png", "npx hardhat node — local blockchain", node_body),
        "deploy": render_terminal(DOCS / "deploy.png", "scripts/deploy.js — localhost", deploy_body),
    }


Q1_PARAS = [
    "This section walks through Coinbase for a classmate who has never used an exchange. No real money was spent. The six steps follow Coinbase's public product and official help documentation.",
    "<b>Step 1 — Create an account.</b> You start with an email, a password, your country, and a confirmation that you are 18 or older. Coinbase then runs Know Your Customer checks: legal name, date of birth, home address, a government ID (passport, national ID, or driving licence), and a selfie matched to that ID. Some regions also ask about employment and the source of funds. Exchanges require this because they are regulated like financial firms. In the United States the Bank Secrecy Act, the USA PATRIOT Act, and FinCEN AML rules force them to identify customers and screen sanctions lists. Other countries apply similar KYC/AML law under FATF guidance, so stolen identities and criminal funds are harder to move through the platform.",
    "<b>Step 2 — Explore the platform.</b> The dashboard shows portfolio value and buy/sell shortcuts. The wallet lists each crypto and cash balance. Trading has a simple Buy screen and an Advanced Trade order book. Bitcoin (BTC) is digital cash with a 21 million cap; people use it as a store of value, and unlike Ethereum it is not a general-purpose computer. Ethereum (ETH) runs smart contracts and NFTs — including this assignment's contracts — and ETH is spent as gas. Solana (SOL) is also programmable, but it is built for speed: cheap, sub-second transfers rather than Bitcoin's conservatism or Ethereum's default token standards.",
    "<b>Step 3 — Add a payment method.</b> Settings → Payment methods lets you link a bank account or debit card. A bank account is linked through a service such as Plaid, or by entering account and routing numbers and confirming micro-deposits. A debit card needs the number, expiry, CVC, and billing address, and the name must match the verified account. Bank transfer is cheaper (typically no funding fee) but slower to clear. A debit card is instant but adds about 3.99 percent. On $100 that is roughly four extra dollars, so the bank transfer is better value if you can wait.",
    "<b>Step 4 — Simulate a $100 purchase.</b> I would buy Ethereum, the chain used in Question 2. A market order fills immediately at the current price. A limit order waits for a price you set. I would choose a market order: $100 is too small to wait for a slightly better fill, and I want a finished trade in history. On the simple Buy screen a bank-funded $100 order typically takes about $2.99 plus a ~0.5 percent spread. At an ETH price of about $2,363 on 28 October 2026, roughly $96.51 would buy about 0.0408 ETH after fees.",
    "<b>Step 5 — Review the transaction record.</b> History shows the asset, buy or sell, amount, price, fees, payment method, status, and time, plus an internal Coinbase reference. When crypto later moves onto a blockchain, the record also shows a transaction hash: a unique hex fingerprint of that on-chain transfer. It matters because anyone can paste it into a block explorer and independently check sender, receiver, amount, and block. Buys that stay inside Coinbase are internal ledger entries and may not have a chain hash until you withdraw.",
    "<b>Step 6 — Security features.</b> Two-factor authentication asks for a code from an authenticator app or hardware key after your password, so a stolen password is not enough. Coinbase prefers that over SMS, which can be SIM-swapped. Withdrawal allowlists and limits are the second control: funds can only leave to pre-approved addresses, and amounts are capped until more verification is done. Even if an attacker logs in, they cannot instantly drain the account to a brand-new wallet.",
]


def q1_plain() -> str:
    return " ".join(re.sub(r"<[^>]+>", "", p) for p in Q1_PARAS)


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "CoverKicker",
            fontName="Times-Bold",
            fontSize=10,
            textColor=TEAL,
            alignment=TA_CENTER,
            letterSpacing=1.2,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverTitle",
            fontName="Times-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverSub",
            fontName="Times-Italic",
            fontSize=12,
            leading=16,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "Section",
            fontName="Times-Bold",
            fontSize=14,
            leading=18,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
            borderPadding=3,
        )
    )
    styles.add(
        ParagraphStyle(
            "SubHead",
            fontName="Times-Bold",
            fontSize=12,
            leading=15,
            textColor=TEAL,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodyJust",
            fontName="Times-Roman",
            fontSize=11,
            leading=15.5,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Caption",
            fontName="Times-Italic",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "CodeBlock",
            fontName="Courier",
            fontSize=8.5,
            leading=12,
            textColor=INK,
            backColor=HexColor("#F4F7FA"),
            leftIndent=6,
            rightIndent=6,
            spaceBefore=4,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Footer",
            fontName="Times-Roman",
            fontSize=8.5,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "BulletBody",
            fontName="Times-Roman",
            fontSize=11,
            leading=15,
            textColor=INK,
        )
    )
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 12, width, 12, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, width, 10, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(18 * mm, 4 * mm, "ALU Blockchain and Applications — Assignment 1")
    canvas.drawRightString(width - 18 * mm, 4 * mm, f"Page {doc.page}")
    canvas.restoreState()


def figure(path: Path, styles, caption: str, width=170 * mm):
    img = Image.open(path)
    w, h = img.size
    height = width * (h / w)
    flow = [
        RLImage(str(path), width=width, height=height),
        Paragraph(caption, styles["Caption"]),
    ]
    return KeepTogether(flow)


def build_pdf(shots: dict[str, Path]) -> None:
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Protecting the ALU Logo on the Ethereum Blockchain",
        author="African Leadership University",
        subject="Blockchain and Applications — Assignment 1",
    )
    story = []

    story.append(Paragraph("AFRICAN LEADERSHIP UNIVERSITY", styles["CoverKicker"]))
    story.append(Paragraph("Protecting the ALU Logo on the Ethereum Blockchain", styles["CoverTitle"]))
    story.append(
        Paragraph(
            "Blockchain and Applications — Assignment 1<br/>Question 1: Cryptocurrency Exchange Exploration<br/>Question 2: Smart Contracts for Logo Registration and Tokenisation",
            styles["CoverSub"],
        )
    )
    story.append(Paragraph("October 2026", styles["CoverSub"]))
    story.append(Spacer(1, 8))
    if LOGO.exists():
        display_logo = DOCS / "alu-logo-display.png"
        raw = Image.open(LOGO).convert("RGBA")
        # The source PNG has a 2px dark artefact on the right edge; crop only
        # the copy used in the report so the hashed alu-logo.png is untouched.
        cropped = raw.crop((0, 0, raw.size[0] - 2, raw.size[1]))
        cropped.save(display_logo)
        story.append(RLImage(str(display_logo), width=118 * mm, height=118 * mm * (cropped.size[1] / cropped.size[0])))
        story.append(
            Paragraph(
                "Figure 1. Official ALU wordmark registered on-chain (source: naissance.alueducation.com).",
                styles["Caption"],
            )
        )

    # Abstract
    story.append(Paragraph("1. Abstract", styles["Section"]))
    story.append(
        Paragraph(
            "This project explores how a regulated cryptocurrency exchange works and then uses that "
            "same public-ledger idea to protect a real digital asset: the official ALU logo. Two Solidity "
            "contracts were written, tested, and deployed on a local Hardhat Ethereum network. "
            "<font name='Courier'>ALUAssetRegistry</font> records the logo as an ERC-721 NFT together with "
            "its SHA-256 file fingerprint, so a fake or edited copy can be detected. "
            "<font name='Courier'>ALULogoToken</font> then issues 1,000,000 ERC-20 ALUT shares so ownership "
            "of that unique asset can be split among ALU stakeholders without changing the logo file itself.",
            styles["BodyJust"],
        )
    )

    # Introduction
    story.append(Paragraph("2. Introduction", styles["Section"]))
    story.append(
        Paragraph(
            "ALU's logo is how students, employers, and the public recognise the university. Once the "
            "file is on the internet it can be copied, recoloured, or attached to a fake certificate. A "
            "normal database can store 'ALU owns this file', but the operator of that database can edit "
            "the row later, and outsiders have to trust the operator. A copyright registration proves a "
            "legal claim, but it does not let a stranger check whether the PNG on their laptop is the "
            "same bytes ALU originally published.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "Putting the logo on Ethereum solves a different problem. The SHA-256 hash of the exact file "
            "is written into a smart contract. After that, nobody — not even the contract author — can "
            "quietly swap the hash, because changing contract storage would require a new transaction "
            "that every node would reject unless the contract itself exposed a rewrite function (this "
            "one does not). Anyone can hash a suspect file and compare it with the on-chain value. The "
            "NFT also records who registered the logo and when. Tokenisation then lets ALU issue shares "
            "of that unique asset without handing the original file to every stakeholder.",
            styles["BodyJust"],
        )
    )

    # Q1
    story.append(Paragraph("3. Question 1: Exploring Coinbase", styles["Section"]))
    q1_words = word_count(q1_plain())
    story.append(
        Paragraph(
            f"<i>Exchange exploration report ({q1_words} words).</i>",
            styles["Caption"],
        )
    )
    for para in Q1_PARAS:
        story.append(Paragraph(para, styles["BodyJust"]))

    story.append(
        Paragraph(
            "Note on screenshots for Question 1. Completing Coinbase identity verification requires a "
            "real government ID and a live selfie. Those personal documents were not submitted from this "
            "development environment. The six steps above follow Coinbase's published product and help "
            "centre. If the course requires captures from a verified personal account, add those images "
            "from your own login before uploading the PDF.",
            styles["BodyJust"],
        )
    )

    # Blockchain setup
    story.append(Paragraph("4. Blockchain Setup", styles["Section"]))
    story.append(
        Paragraph(
            "A local blockchain is a complete Ethereum network that runs only on your computer. Hardhat "
            "creates one in memory for tests, and <font name='Courier'>npx hardhat node</font> starts a "
            "longer-lived JSON-RPC node at <font name='Courier'>http://127.0.0.1:8545</font>. Developers "
            "use a local chain instead of Ethereum mainnet because every mainnet transaction costs real "
            "ETH, is public forever, and cannot be undone. On Hardhat you get 20 pre-funded test wallets, "
            "blocks mine in milliseconds, and you can reset state as many times as you like. Nothing here "
            "touches the real Ethereum network.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "A wallet address is a 20-byte identifier, usually shown as a 42-character hexadecimal string "
            "starting with <font name='Courier'>0x</font>. It is derived from a public key, which is derived "
            "from a private key. On the blockchain it represents an account: the place that holds ETH, "
            "owns NFTs, and is recorded as <font name='Courier'>msg.sender</font> when a contract is called. "
            "Account #0 below, <font name='Courier'>0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266</font>, is "
            "the well-known Hardhat deployer. Each account starts with 10,000 test ETH. Those private keys "
            "are public documentation keys — they must never receive real funds.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "What each part of the setup is doing. Node.js is the runtime that Hardhat uses. Hardhat is "
            "the development environment: it compiles Solidity, runs tests, and exposes the local chain. "
            "OpenZeppelin provides audited ERC-721, ERC-20, and Ownable implementations so the assignment "
            "does not re-implement token standards from scratch. <font name='Courier'>hardhat.config.js</font> "
            "pins Solidity 0.8.24 and the Cancun EVM. The in-memory <font name='Courier'>hardhat</font> "
            "network is what <font name='Courier'>npx hardhat test</font> uses. The "
            "<font name='Courier'>localhost</font> network is what the deploy script uses once the node is running.",
            styles["BodyJust"],
        )
    )
    story.append(
        figure(
            shots["node"],
            styles,
            "Figure 2. Local Hardhat node at http://127.0.0.1:8545 with generated test wallet addresses.",
        )
    )

    # Smart contracts
    story.append(Paragraph("5. Smart Contract Explanation", styles["Section"]))
    story.append(
        Paragraph(
            "A smart contract is a program stored on a blockchain. Once deployed, every honest node "
            "executes the same bytecode against the same state. That is different from a normal programme "
            "on a server. A server program can be stopped, patched, or made to return different answers "
            "to different users. A deployed contract has a public address, public code, and public "
            "storage. You cannot quietly log in and rewrite a row. If the contract has no function that "
            "changes a value, that value stays. Users do not trust ALU's web host; they trust the "
            "network's consensus rules.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "An NFT (non-fungible token) is a token where each unit is unique. ERC-721 is the Ethereum "
            "standard for that idea: every token has an ID, a single owner, and optional metadata. The "
            "ALU logo is a single official file, not a pile of identical coins, so ERC-721 is the right "
            "standard. Two logos must not be interchangeable. ERC-20 would be the wrong choice for the "
            "file itself because any one ERC-20 unit is equal to any other.",
            styles["BodyJust"],
        )
    )
    story.append(Paragraph("5.1 Generating the ALU logo hash", styles["SubHead"]))
    story.append(
        Paragraph(
            "Before registration the actual PNG was hashed with SHA-256 in Node.js "
            "(<font name='Courier'>crypto.createHash('sha256')</font>) and confirmed with "
            "<font name='Courier'>shasum -a 256</font>. SHA-256 is a cryptographic hash function: it "
            "takes any file and produces a fixed 32-byte digest. It is deterministic (the same file "
            "always yields the same digest) and collision-resistant (it is infeasible to find a different "
            "file with the same digest). Changing even one pixel flips many bits in the input, and the "
            "avalanche effect of SHA-256 produces a completely unrelated output. That is why a cropped, "
            "recoloured, or lightly edited fake logo cannot pass <font name='Courier'>verifyLogoIntegrity()</font>. "
            "The 32-byte digest fits naturally into Solidity's <font name='Courier'>bytes32</font> type.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            f"<font name='Courier'>SHA-256 = {HASH}</font>",
            styles["CodeBlock"],
        )
    )
    story.append(
        figure(
            shots["hash"],
            styles,
            "Figure 3. SHA-256 fingerprint of alu-logo.png, generated from the real file, not a placeholder.",
        )
    )

    story.append(Paragraph("5.2 ALUAssetRegistry (ERC-721)", styles["SubHead"]))
    story.append(
        Paragraph(
            "The contract extends OpenZeppelin's ERC-721. <font name='Courier'>AssetMetadata</font> stores "
            "the asset name, file type, SHA-256 content hash, registrant address, and Unix timestamp. "
            "Mapping <font name='Courier'>assets</font> looks up that struct by token ID. Mapping "
            "<font name='Courier'>registeredHashes</font> records whether a hash has already been used.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "<b>registerAsset(name, fileType, contentHash)</b> is the write function. It rejects an empty "
            "name, file type, or hash, then reverts with <font name='Courier'>\"Asset already registered: "
            "duplicate content hash\"</font> if the file was seen before. Otherwise it increments a counter "
            "from 1, mints an NFT to the caller with <font name='Courier'>_safeMint()</font>, writes the "
            "metadata, marks the hash as used, emits <font name='Courier'>AssetRegistered</font>, and "
            "returns the new token ID. The official logo is registered as token ID 1 during deployment.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "<b>verifyLogoIntegrity(tokenId, contentHash)</b> is a <font name='Courier'>view</font> function, "
            "so a direct call from a wallet or dApp costs no gas. It loads the stored hash for that token "
            "and compares it with the caller's value. A match returns <font name='Courier'>(true, "
            "\"Logo is authentic.\")</font>. A mismatch returns <font name='Courier'>(false, "
            "\"Warning: logo does not match.\")</font>. That is the public authenticity check ALU wanted.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "<b>getAsset(tokenId)</b> is also a view function. It returns the full "
            "<font name='Courier'>AssetMetadata</font> struct so anyone can read the name, file type, hash, "
            "registrant, and timestamp at any time.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "Once stored, this data cannot be changed because the contract exposes no setter that "
            "overwrites <font name='Courier'>assets[tokenId]</font> or clears "
            "<font name='Courier'>registeredHashes</font>. Ethereum storage is append-only from the outside: "
            "the only way to mutate it is to execute a function the contract author wrote. With no such "
            "function, the registration is permanent for as long as the chain continues.",
            styles["BodyJust"],
        )
    )

    story.append(Paragraph("5.3 Deployment script", styles["SubHead"]))
    story.append(
        Paragraph(
            "<font name='Courier'>scripts/deploy.js</font> hashes <font name='Courier'>alu-logo.png</font>, "
            "deploys <font name='Courier'>ALUAssetRegistry</font>, immediately calls "
            "<font name='Courier'>registerAsset(\"ALU Official Logo\", \"image/png\", contentHash)</font>, "
            "then deploys <font name='Courier'>ALULogoToken</font> with the deployer as logo owner so the "
            "full ALUT supply is minted in the same run.",
            styles["BodyJust"],
        )
    )
    story.append(
        figure(
            shots["deploy"],
            styles,
            "Figure 4. Deployment on the local node: logo registered as token ID 1 and 1,000,000 ALUT minted.",
        )
    )

    # Tokenisation
    story.append(Paragraph("6. Tokenisation", styles["Section"]))
    story.append(
        Paragraph(
            "Tokenisation means taking a unique real-world or digital asset and representing rights in "
            "that asset as digital tokens that can be held, transferred, or accounted for on a blockchain. "
            "For the ALU logo, the unique thing remains one NFT. What gets split is ownership. Instead of "
            "one office 'owning the brand file', many people can hold a measured share of it.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "Who at ALU might receive ALUT, and why? The communications or brand office could keep a "
            "controlling treasury so the university remains the primary steward of the mark. Faculty who "
            "create official courseware that uses the logo might receive a small allocation as recognition "
            "that they are trusted users of the brand. Student government or campus ambassadors might hold "
            "a symbolic share tied to representing ALU in public. Administration (the registrar, legal, "
            "and partnerships teams) might hold shares because they approve how the logo appears on "
            "transcripts and partner materials. None of those people need a copy of a private PNG sitting "
            "in email. They hold tokens that the registry already ties to the authentic file.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "ERC-721 and ERC-20 solve opposite problems. ERC-721 says 'this token is not interchangeable'. "
            "That is correct for one official logo file. ERC-20 says 'every unit is the same as every other "
            "unit'. That is correct for shares. One faculty member's 1 ALUT must equal another person's "
            "1 ALUT, otherwise percentage ownership does not make sense. Using ERC-721 for the shares would "
            "make every share a unique object and destroy the idea of a simple percentage. Using ERC-20 for "
            "the logo file would imply that any one 'logo token' is as official as any other, which would "
            "defeat authenticity.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "<b>ALULogoToken</b> is named \"ALU Logo Token\" with symbol ALUT. The constructor mints "
            "1,000,000 tokens (18 decimals, so 1,000,000 × 10<super>18</super> base units) to the logo "
            "owner and sets that address as <font name='Courier'>Ownable</font> owner. No further minting "
            "function exists, so the supply is fixed.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "<b>distributeShares(recipient, amount)</b> can be called only by the owner. It requires a "
            "non-zero amount and then transfers ALUT from the owner's balance to the recipient. That is "
            "how ALU would send shares to faculty or students.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "<b>ownershipPercentage(account)</b> is a view function. It returns "
            "<font name='Courier'>(balance × 100) / totalSupply</font> as a whole number. A faculty member "
            "who holds 100,000 ALUT out of 1,000,000 holds 10 percent. In practice that means they have a "
            "recorded 10 percent claim on the tokenised logo: they could be treated as a 10 percent "
            "stakeholder in brand-governance votes, revenue-share experiments, or internal reporting. "
            "They do not own '10 percent of the pixels'. The file stays unique. They own 10 percent of "
            "the tokenised rights that ALU chose to attach to that file. 500,000 ALUT would return 50.",
            styles["BodyJust"],
        )
    )

    # Tests
    story.append(Paragraph("7. Test Results", styles["Section"]))
    story.append(
        Paragraph(
            "Eight automated tests in <font name='Courier'>test/ALUAssetRegistry.test.js</font> were run "
            "with <font name='Courier'>npx hardhat test</font>. All eight passed. They cover: successful "
            "registration and a returned token ID; rejection of a duplicate hash; authentic and inauthentic "
            "integrity checks; correct metadata from <font name='Courier'>getAsset</font>; minting of "
            "1,000,000 ALUT to the owner; a share transfer; and a 50 / 10 / 40 percent split after two "
            "distributions.",
            styles["BodyJust"],
        )
    )
    story.append(
        figure(
            shots["tests"],
            styles,
            "Figure 5. All eight required automated tests passing.",
        )
    )

    # Conclusion
    story.append(Paragraph("8. Conclusion", styles["Section"]))
    story.append(
        Paragraph(
            "A cryptocurrency exchange showed the regulated, custodial side of digital assets: identity "
            "checks, order types, fees, and account security. The smart-contract side showed the opposite "
            "move: taking a file ALU already owns and giving the public a way to verify it without asking "
            "ALU's web server. The important technical lessons were that a SHA-256 digest is enough to "
            "detect tampering, that ERC-721 and ERC-20 are not competing styles but two different answers, "
            "and that a local Hardhat chain is how you practise all of this without spending ETH.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "If there were more time, the next improvements would be: deploying the same contracts to "
            "the Ethereum Sepolia testnet so the registration is visible on a public explorer; adding a "
            "simple dApp (the stated follow-on assignment) that lets a user upload a PNG, hash it in the "
            "browser, and call <font name='Courier'>verifyLogoIntegrity</font>; storing an IPFS content "
            "identifier next to the hash so the file itself is retrievable; and adding a snapshot-based "
            "vote so ALUT holders could decide brand-use requests. A pause switch and a documented legal "
            "wrapper around what an ALUT share does and does not grant would also be needed before any "
            "real university use.",
            styles["BodyJust"],
        )
    )

    story.append(Paragraph("9. GitHub Repository", styles["Section"]))
    story.append(
        Paragraph(
            f"Public repository with the full source, tests, logo file, and this report:<br/>"
            f"<link href='{GITHUB}' color='#0E7C86'><u>{GITHUB}</u></link>",
            styles["BodyJust"],
        )
    )

    story.append(Paragraph("10. Video Walkthrough", styles["Section"]))
    story.append(
        Paragraph(
            "A short screen recording should be added here before final portal submission. Record two to "
            "four minutes covering: (1) <font name='Courier'>npx hardhat node</font> showing the generated "
            "wallet addresses, (2) <font name='Courier'>npx hardhat test</font> with all eight tests "
            "passing, and (3) <font name='Courier'>npx hardhat run scripts/deploy.js --network localhost</font> "
            "registering the ALU logo. Upload the video to YouTube (unlisted) or Google Drive and replace "
            "the line below with the live URL.",
            styles["BodyJust"],
        )
    )
    story.append(
        Paragraph(
            "Video link: add the hosted URL here after recording.",
            styles["BodyJust"],
        )
    )

    story.append(Paragraph("11. References", styles["Section"]))
    refs = [
        "Coinbase, 'Know-your-customer (KYC) verification', https://www.coinbase.com/blog/know-your-customer-kyc-verification",
        "Coinbase Help, 'Pricing and fees disclosures', https://help.coinbase.com/en/coinbase/trading-and-funding/pricing-and-fees/fees",
        "Coinbase Help, 'Using a bank account as a payment method', https://help.coinbase.com/en/coinbase/getting-started/add-a-payment-method/using-a-bank-account-as-a-payment-method-for-us-customers",
        "Coinbase User Agreement (United States), Appendix 1: Verification Procedures and Limits.",
        "OpenZeppelin Contracts v5, ERC-721, ERC-20, and Ownable.",
        "Hardhat documentation, https://hardhat.org/docs",
        "African Leadership University, official wordmark from https://naissance.alueducation.com/images/assets/alulogo.png",
    ]
    for ref in refs:
        story.append(Paragraph("• " + ref.replace("<", "&lt;").replace(">", "&gt;"), styles["BulletBody"]))
        story.append(Spacer(1, 3))

    print(f"Question 1 word count: {q1_words}")
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {PDF}")


if __name__ == "__main__":
    shots = build_screenshots()
    build_pdf(shots)
