import asyncio
import time

from brainyflow import SequentialBatchNode, ParallelBatchNode, Flow

####################################
# Dummy async function (1s delay)
####################################
async def dummy_llm_summarize(text):
    """Simulates an async LLM call that takes 1 second."""
    await asyncio.sleep(1)
    return f"Summarized({len(text)} chars)"

###############################################
# 1) SequentialBatchNode (sequential) version
###############################################

class SummariesNode(SequentialBatchNode):
    """
    Processes items sequentially in an async manner.
    The next item won't start until the previous item has finished.
    """

    async def prep_async(self, shared):
        # Return a list of items to process.
        # Each item is (filename, content).
        return list(shared["data"].items())

    async def exec_async(self, item):
        filename, content = item
        print(f"[Sequential] Summarizing {filename}...")
        summary = await dummy_llm_summarize(content)
        return (filename, summary)

    async def post_async(self, shared, prep_res, exec_res_list):
        # exec_res_list is a list of (filename, summary)
        shared["sequential_summaries"] = dict(exec_res_list)
        return "done_sequential"

###############################################
# 2) ParallelBatchNode (concurrent) version
###############################################

class SummariesAsyncParallelNode(ParallelBatchNode):
    """
    Processes items in parallel. Many LLM calls start at once.
    """

    async def prep_async(self, shared):
        return list(shared["data"].items())

    async def exec_async(self, item):
        filename, content = item
        print(f"[Parallel] Summarizing {filename}...")
        summary = await dummy_llm_summarize(content)
        return (filename, summary)

    async def post_async(self, shared, prep_res, exec_res_list):
        shared["parallel_summaries"] = dict(exec_res_list)
        return "done_parallel"

###############################################
# Demo comparing the two approaches
###############################################

async def main():
    # We'll use the same data for both flows
    shared_data = {
        "data": {
            "file1.txt": "Hello world 1",
            "file2.txt": "Hello world 2",
            "file3.txt": "Hello world 3",
        }
    }

    # 1) Run the sequential version
    seq_node = SummariesNode()
    seq_flow = Flow(start=seq_node)

    print("\n=== Running Sequential (SequentialBatchNode) ===")
    t0 = time.time()
    await seq_flow.run_async(shared_data)
    t1 = time.time()

    # 2) Run the parallel version
    par_node = SummariesAsyncParallelNode()
    par_flow = Flow(start=par_node)

    print("\n=== Running Parallel (ParallelBatchNode) ===")
    t2 = time.time()
    await par_flow.run_async(shared_data)
    t3 = time.time()

    # Show times
    print("\n--- Results ---")
    print(f"Sequential Summaries: {shared_data.get('sequential_summaries')}")
    print(f"Parallel Summaries:   {shared_data.get('parallel_summaries')}")

    print(f"Sequential took: {t1 - t0:.2f} seconds")
    print(f"Parallel took:   {t3 - t2:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())