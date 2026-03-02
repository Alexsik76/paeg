# Electronic Voting Simulator

A modular, scalable Streamlit application for simulating Electronic Voting Protocols.

## Features

- **No Database:** Uses `streamlit.session_state` to persist data during the session.
- **Configuration Driven:** UI and protocol parameters are defined in `config.yaml`.
- **Separation of Concerns:** Clean architecture separating Streamlit UI, business logic, and cryptography.
- **Cryptographic Foundations:** Implements RSA key generation, encryption, decryption, signing, and verification.

---

## 🛠️ Deployment & Setup (Розгортання)

**Prerequisites:** Python 3.9+ is recommended.

1. **Activate the Virtual Environment:**
   If you have already created a virtual environment named `.venv`, activate it:
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     .\.venv\Scripts\activate.bat
     ```

2. **Install Dependencies:**
   Install the required Python packages specified in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration (Конфігурування)

The application is fully driven by the `config.yaml` file located in the root directory.

### Structure of `config.yaml`

You can define multiple labs and their settings. Here is an explanation of the fields:

- `labs`: A list of different lab protocols.
  - `id`: Unique identifier for the lab.
  - `name`: Display name in the UI.
  - `protocol`: Internal identifier for the protocol logic (e.g., `simple`).
  - `settings`:
    - `num_voters`: Total number of simulated basic voters.
    - `candidates`: List of available candidates to vote for.
  - `scenarios`: Test cases available in the UI.
    - `id`: Action identifier (e.g., `normal_vote`, `double_vote`, `tampered_ballot`, `unregistered_voter`).
    - `name`: Display name of the scenario.
    - `description`: Brief explanation of what the test does.

**To modify the simulation:** Simply edit `config.yaml` (e.g., add new candidates or change the number of voters), save the file, and refresh the Streamlit page.

---

## 🚀 Running the Application (Запуск)

1. Ensure your virtual environment is activated.
2. Run the Streamlit application:
   ```bash
   streamlit run main.py
   ```
3. A browser window should open automatically at `http://localhost:8501`.

### How to Test (Як тестувати)

1. **Select a Protocol:** In the sidebar, select the lab you want to simulate (e.g., "Lab 1: Simple Protocol").
2. **Control Panel Tab:**
   - Choose a specific test scenario (e.g., "Normal Vote" or "Tampered Ballot").
   - Select a candidate.
   - Select the voter performing the action.
   - Click **"Execute Scenario"**.
3. **Terminal Logs Tab:** Switch to this tab to see the cryptographic steps happening under the hood (signing, encrypting, decrypting, verifying).
4. **Results Tab:** View the live tally of the election votes. You will notice that invalid votes (like tampered ballots or double voting) will _not_ be added to the tally.
