#!/bin/bash
source $(dirname $0)/run-lambda.sh > /dev/null 2>&1 && $(dirname $0)/get-lambda-logs.sh
