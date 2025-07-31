# 🧠 AI Customer Support Orchestrator (with MCP)

This project is an **autonomous AI-powered customer support orchestrator**, built to classify customer queries, create Jira tickets, notify support teams via Slack, and email users automatically using **Model Context Protocol (MCP)**.

It showcases an **industrial-grade agentic backend** with retry logic, logging, streaming, and dynamic context sharing across steps.

---

## 🚀 Features

- ✅ Process user queries with contextual memory
- 🧠 Classify issue type using DeepSeek LLM API
- 🧾 Create Jira tickets with formatted issue metadata
- 💬 Notify Slack channel (support team)
- 📧 Draft and send support emails automatically
- 📁 CSV-based batch processing
- 🔁 Built-in retry logic, timeouts, and structured logging

---

## 📦 Folder Structure

```
backend/
│
├── mcp_server/
│   ├── models/               # SQLAlchemy models (CRM, Ticket)
│   ├── services/             # Services (LLM, Slack, Jira, Email)
│   ├── utils/                # DB init and utility files
│   └── server.py             # MCP tools and main logic
│   └── init_db.py            # Creating CRM table using CRM.csv and ticket table in Postgres.
|
├── data/
│   └── customer_query.csv    # Input file for batch testing
    └── CRM.csv               # Loaded into the CRM table in the PostgreSQL database
│
├── .env                      # Environment variables
└── README.md                 # You're reading it
```

---

## ⚙️ Tech Stack

- Python 3.11+
- FastMCP (`mcp[fastapi]`)
- SQLAlchemy + PostgreSQL
- DeepSeek LLM API
- Slack Webhook
- Jira Cloud REST API
- Mailtrap SMTP for emails
- Pandas for batch input
- Tenacity for retry logic

---

## 🧬 MCP vs Traditional API Calls

| Aspect | Traditional API | Model Context Protocol (MCP) |
|--------|------------------|------------------------------|
| State Management | Manual | Implicit via context |
| Tool Calling | Hardcoded | Declarative with metadata |
| Streaming & Logging | Custom logic | Built-in |
| Reusability | Low | High (tools are modular) |
| Memory between calls | Requires DB/state logic | Handled by MCP |

MCP allows us to treat tools like autonomous steps in a pipeline with **streamable inputs, LLM-friendly I/O, and fault tolerance**.

---

## 🛠️ Installation

```bash
git clone https://github.com/tanmayypramanick/mcp-based-customer-support-orchestrator.git
cd mcp-based-customer-support-orchestrator/backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in `backend/`:

```dotenv
# 🔐 LLM API (DeepSeek)
DEEPSEEK_API_KEY=your_deepseek_api_key

# 📧 Email
EMAIL_USER=your_username
EMAIL_PASSWORD=your_password
EMAIL_HOST=your_email_host
EMAIL_PORT=ypur_port
EMAIL_FROM=your@email.com

# 📌 Jira
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USER_EMAIL=your@email.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=your_project_key

# 💬 Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# 🧪 CSV path
CUSTOMER_QUERY_CSV=../data/customer_query.csv

# CRM Data
DATABASE_URL=postgresql://yourusername:yourpassword@yourlocalhost/support_orchestrator
```

---

## 🧪 How to Run

### 1. Run the MCP Server

```bash
python mcp_server/server.py
```

This will start the FastMCP server.

---
### 2. Install and Run MCP Inspector (Optional)

```bash
npm install -g mcp-inspector
```
then, run the MCP Inspector UI:
```bash
mcp dev mcp_server/server.py
```
What this does:
- Starts the MCP FastAPI server from `server.py`
- Automatically launches the MCP Inspector UI in your browser
- Lets you test each tool interactively.

### 3. Interact via Inspector or CLI

```bash
# For one-off ticket creation
> process_query(customer_email="abc@example.com", ticket_description="I have a problem with the {product_purchased}", product_purchased="Xbox")

# For batch mode:
> run_batch_pipeline(num_queries=1)
```


# Make sure to create PostgreSQL database before running MCP server.

Make sure PostgreSQL is installed and running. Then open your terminal and run:

```bash
psql -U postgres
```
Inside the `psql` prompt, run:

```bash
CREATE DATABASE support_orchestrator;
```

Then, Initialize Tables

```bash
cd backend
python -m app.init_db
```
This will:
- Create the crm and ticket tables using SQLAlchemy.
- Load data from data/CRM.csv into the CRM table.

You should see log messages confirming successful database initialization.

---

## 🧠 How It Works

1. **User Query** is read from CSV or CLI
2. `process_query()` creates ticket with metadata
3. `classify_issue()` uses DeepSeek to predict category (e.g., Billing, Technical)
4. `create_jira()` creates Jira ticket with summary + rich body
5. `notify_slack()` sends a Slack message to team
6. `draft_email()` uses template logic to create a professional response
7. `send_email_tool()` sends it via SMTP (Mailtrap)
8. `run_batch_pipeline()` triggers a full autonomous loop over multiple entries. Calls each of the tools in sequence for each query.


Everything is orchestrated via **MCP tools** with built-in retry logic, error logging, and modular structure.

---

## 🖼️ Screenshots

- 📸 **MCP Inspector showing tool streaming**
  
![MCP Inspector](./screenshots/MCP-Inspector.png)

- 🧾 **Jira Ticket**
  
![Jira Ticket](./screenshots/Jira-Ticket.png)

- 💬 **Slack Message**
  
![Slack Notification](./screenshots/Slack-Message.png)

- 📧 **Drafted Email**
  
![Email Draft](./screenshots/Drafted-Email.png)

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 👤 Author

**Developed by Tanmay Pramanick**

📧 tanmaypramanick06@gmail.com 
🔗 https://www.linkedin.com/in/tanmaypramanick/
🔗 https://tanmayypramanick.github.io/

---

## 🙏 Attribution

If you use or adapt this codebase, please consider crediting the original author.

Drop a ⭐ on GitHub if this project helped you!

---

## 🧠 Inspiration

This project demonstrates a real-world use of **agentic workflows, declarative tool design, and autonomous pipelines** with MCP, perfect for production-grade support systems.

If you're hiring a Software Engineer passionate about LLMs + automation, reach out!

