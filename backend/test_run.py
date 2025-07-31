from mcp_server.server import run_batch_pipeline

if __name__ == "__main__":
    result = run_batch_pipeline(num_queries=1)
    print(result)
