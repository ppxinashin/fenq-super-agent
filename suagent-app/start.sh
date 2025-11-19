rm -rf .next
npm run build
nohup npm run start > logs/suagent-app.log 2>&1 &