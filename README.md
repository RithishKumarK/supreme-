

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Stack](#stack)
- [Setting Up](#setting-up)
- [Run Locally](#run-locally)
- [Contributors](#contributors)
- [License](#license)
- [Troubleshooting](#troubleshooting)

## Introduction

**ArchFlow** is a powerful tool that converts a given text prompt into an SQL query, which in turn creates tables in the backend. It enables seamless database schema generation by leveraging AI-driven natural language processing and database automation. The project is built for developers, data engineers, and database administrators to streamline SQL table creation.

## Requirements

- Python >= 3.8
- Additional dependencies specified in `requirements.txt`

### Core Technologies
- **Backend** (Node.js + Express)
- Node.js – Runtime environment for JavaScript on the server.
- Express.js – Backend framework for handling API requests.
- CORS – Middleware to enable cross-origin requests.
- Supabase (@supabase/supabase-js) – Open-source alternative to Firebase, used for database operations.
- **Frontend** (React.js)
- React.js – Frontend framework for building UI.
- React Components – Modular UI structure (e.g., SQLQueryInterface.js).
- Lucide-react – Icon library for UI enhancement.t

## Setting Up

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/archflow.git
   ```
2. Navigate into the project directory:
   ```sh
   cd archflow
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Run Locally

### Running with Python
```sh
python archflow.py
```

## Contributors

<a href="https://github.com/your-repo/archflow/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=your-repo/archflow" />
</a>

## License

[**MIT**](LICENSE)

## Troubleshooting

### Issue: Dependencies not installing
Ensure you are using Python 3.8 or later and have `pip` updated:
```sh
pip install --upgrade pip
```
