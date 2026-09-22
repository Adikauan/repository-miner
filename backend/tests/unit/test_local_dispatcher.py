from repository_miner.executions.infrastructure.local_dispatcher import LocalExecutionDispatcher, RunExecution


def test_local_dispatcher_keeps_durable_command_identity():
    command = RunExecution("execution-1")
    assert command.execution_id == "execution-1"
    assert LocalExecutionDispatcher.__name__ == "LocalExecutionDispatcher"
