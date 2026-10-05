#!/bin/bash
# restart aimock with fixtures dir
E=/workspace/harness-faults; export PATH=/opt/node22/bin:$PATH
[ -f $E/mock.pid ] && kill $(cat $E/mock.pid) 2>/dev/null; sleep 1
cd $E; setsid nohup node_modules/.bin/llmock -p 4010 -f fixtures --log-level info > $E/mock.log 2>&1 < /dev/null &
echo $! > $E/mock.pid; sleep 3; curl -s localhost:4010/health; echo
