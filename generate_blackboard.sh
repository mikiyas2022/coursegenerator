#!/bin/bash
# generate_blackboard: Generate a silent blackboard Q&A solution video.
# All audio/TTS is DISABLED. The output is a pure chalk-on-blackboard animation.

if [ -z "$1" ]; then
    echo "Usage: ./generate_blackboard.sh \"<Question Text>\" [\"<Optional Answer>\"] [\"<Subject Grade>\"]"
    echo "Example: ./generate_blackboard.sh \"A 10kg block slides down a 30° incline. Find its acceleration.\" \"5.0 m/s²\" \"Physics Grade 12 EUEE 2025\""
    exit 1
fi

QUESTION="$1"
ANSWER="${2:-}"
SUBJECT="${3:-}"

curl -N -X POST http://127.0.0.1:8205/generate_full \
     -H "Content-Type: application/json" \
     -d "{
           \"topic\": \"$QUESTION\",
           \"question\": \"$QUESTION\",
           \"correct_answer\": \"$ANSWER\",
           \"subject_grade\": \"$SUBJECT\",
           \"audience\": \"High School (Grade 7–12)\",
           \"style\": \"Blackboard Q&A\",
           \"mode\": \"blackboard\",
           \"silent\": true,
           \"tts_enabled\": false,
           \"run_postprod\": true
         }"
