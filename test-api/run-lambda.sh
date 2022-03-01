#!/bin/bash
curl -X POST https://8ry32om98l.execute-api.eu-west-3.amazonaws.com/api/ -H 'Content-Type: application/json' -d '{"risk_preference": 36, "monthly_savings": 5, "goal_price": 1300, "current_savings": 180, "tax_system": "netherlands"}'
