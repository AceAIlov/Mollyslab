Installation Guide — Azumi (CLI + API)

Azumi is a hybrid emotional agent built on Kimi K2, combining a Rust-based CLI and a FastAPI backend.
Follow the steps below to install, configure, and run the system locally or in Docker.

1. Prerequisites

Before you begin, ensure you have the following installed:

Tool	Version	Purpose
Python	3.11+	Runs the FastAPI backend
Rust / Cargo	Stable	Compiles the Azumi CLI
Docker (optional)	Latest	To run Azumi in a container
Git	Latest	To clone and manage the repository
2. Clone the Repository
git clone https://github.com/yourname/azumi.git
cd azumi

3. Set Environment Variables

Create a local .env file by copying the example:

cp .env.example .env


Edit .env and insert your Kimi K2 credentials:

KIMI_API_KEY=your_kimi_k2_api_key_here
AZUMI_MODE=development
PORT=8000

4. Install the Backend (FastAPI)

Set up the Python environment and install dependencies:

pip install -r requirements.txt


Then start the backend server:

uvicorn api.main:app --reload


By default, Azumi will be available at:

http://localhost:8000


Endpoints:

POST /emotion → Generates emotional response

GET /memory → Returns emotional memory thread

5. Build the CLI (Rust)

Navigate to the CLI directory and build:

cd cli
cargo build --release


Then run Azumi from the terminal:

cargo run -- run "hello azumi"


Expected output:

感情: curiosity  温度: 0.42
応答: Azumi (Kimi K2) reflects on 'hello azumi' and feels curiosity.
