#!/bin/bash
cd /Users/klsandbox/Claude/mdql
./implementations/prototypes/swift-mdql/.build/debug/mdql-demo &
PID=$!
sleep 2
if kill -0 $PID 2>/dev/null; then
  echo "Process still running, killing it..."
  kill $PID
  echo "FAILED: Process hangs or crashes"
  exit 1
else
  wait $PID
  EXIT_CODE=$?
  echo "Process exited with code $EXIT_CODE"
  exit $EXIT_CODE
fi
