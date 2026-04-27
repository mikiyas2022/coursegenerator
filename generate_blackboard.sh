#!/bin/bash
# generate_blackboard: Test command to generate a silent blackboard solution video for a given question.

if [ -z "$1" ]; then
    echo "Usage: ./generate_blackboard.sh \"<Question Text>\""
    echo "Example: ./generate_blackboard.sh \"A 10kg block slides down a 30 degree incline. What is its acceleration?\""
    exit 1
fi

QUESTION="$1"

# We will just call the orchestrator's generate_full endpoint with mode = blackboard
curl -N -X POST http://127.0.0.1:8205/generate_full \
     -H "Content-Type: application/json" \
     -d "{
           \"topic\": \"$QUESTION\",
           \"audience\": \"High School (Grade 7–12)\",
           \"style\": \"Blackboard Q&A\",
           \"mode\": \"blackboard\"
         }"
