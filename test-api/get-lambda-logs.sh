#!/bin/bash
log_stream_name=$(aws logs describe-log-streams --log-group-name /aws/lambda/hypofin-dev --profile $profile | grep "logStreamName" | tail -1 | sed 's/^.*: "\(.*\)".*/\1/')
aws logs get-log-events --profile $profile --log-group-name /aws/lambda/hypofin-dev --log-stream-name $log_stream_name --limit 10 | grep '"message":' | sed -E 's/^\s*"message": "(.*)\\n",$/\1/' | xargs -0 echo -e
