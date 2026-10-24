# Deploy on AWS (EC2 + S3), configuration hidden

Written guide. Nothing here has been run on AWS. The local parts (MySQL store code, `--lock-config`, the publish script's dry run) are tested; a real EC2 box, MySQL server, S3 and nginx are not.

What you get: one EC2 box running the app behind nginx, chat only (the Configuration page returns 404), data in MySQL on the same box, and nightly backups copied to S3. Costs are unverified. Check current EC2, storage, public IPv4, transfer and S3 charges before provisioning.

## 1. One-time AWS setup (you do this, in the console)
1. EC2: launch Ubuntu 24.04, `t3.small`, 20 GB disk. Security group: allow 22 (your IP only), 80 and 443.
2. S3: create a private bucket for backups. Give the instance an IAM role with `s3:PutObject` and `s3:ListBucket` on that bucket only.
3. Elastic IP so the address does not change. Optional: a domain pointed at it.

## 2. Prepare the box
```
sudo apt update && sudo apt install -y python3 python3-venv rsync nginx mysql-server awscli certbot python3-certbot-nginx
sudo mysql -e "CREATE DATABASE chatify CHARACTER SET utf8mb4; CREATE USER 'chat'@'localhost' IDENTIFIED BY 'CHOOSE-A-PASSWORD'; GRANT ALL ON chatify.* TO 'chat'@'localhost';"
sudo mkdir -p /opt/chatify && sudo chown ubuntu /opt/chatify
sudo tee /etc/chatify.env >/dev/null <<'ENV'
OPENAI_API_KEY=your-key
CHATIFY_DB_URL=mysql://chat:CHOOSE-A-PASSWORD@127.0.0.1:3306/chatify
CHATIFY_CONFIG=off
ENV
sudo chmod 600 /etc/chatify.env
```
Keys and the DB password live only in `/etc/chatify.env`, never in the repo. If the password has special characters, URL-encode them (`@` is `%40`).

## 3. Install the service and nginx
```
sudo cp deploy/chatify.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable chatify
```
nginx site (`/etc/nginx/sites-available/chatify`, then link it and reload):
```
server { listen 80; server_name _;
  location / { proxy_pass http://127.0.0.1:8100; proxy_set_header Host $host; proxy_buffering off; proxy_read_timeout 300s; } }
```
`proxy_buffering off` keeps answers streaming. For https run `sudo certbot --nginx` once you have a domain.

## 4. Publish (and every update after)
On your laptop: `cp deploy/publish.env.example deploy/publish.env`, fill in the host and key, then
```
deploy/publish.sh          # shows the plan, changes nothing
deploy/publish.sh --yes    # tests, optional local-file backup, copy, restart, wait for health
```
The script only talks to a box that already exists. It does not create anything in AWS. The service selects `apps/dietchat/app.yaml`; edit the service to use a different app, and set `APP_DATA_DIR` in publish.env to that app's data directory. Optional publish backups copy only local app files and stop publication if the backup fails. They do not back up MySQL; use the separate database dump below.

## 4a. Check for active builds before a restart or deploy
Build with AI jobs run in server memory. Where the data directory persists (this EC2 setup), completed draft areas are checkpointed to `<data>/build-checkpoints/` after every part; after a restart, starting a build with the same brief resumes from those kept areas instead of starting over, and says so in the job notice. Checkpoints carry no keys, provider settings or configs - only draft text, errors and call counts - and are deleted when the build finishes or is cancelled. They do not help on ephemeral filesystems (a free Render instance without a disk loses them with the restart). A restart still discards the in-flight parts themselves, so check first:
```
GET /api/settings/build/active     # signed in as the app owner
```
The response is `{"active": bool, "running_total": N, "mine": [...]}`. `running_total` counts every running build on the server, including other users' builds as a bare count only - their briefs, configs and drafts are never included. `mine` lists only your own running builds with id, phase and progress. If `active` is true, wait and re-check until it is false, or ask the build's owner to cancel it.

This check is a preflight snapshot, not a lock: a build can start in the gap between your check and the restart. Re-check immediately before you confirm the deploy or `systemctl restart`, and prefer low-traffic windows. The same check applies to a Render manual deploy (no shell needed - it is a plain authenticated request in the browser or with curl).

## 5. Backups
```
mysqldump chatify | gzip | aws s3 cp - s3://YOUR-BUCKET/chatify-$(date +%F).sql.gz
```
Put that in a daily cron on the box.

## MySQL notes
- `CHATIFY_DB_URL` set and reachable: MySQL is used. Missing, wrong or unreachable: the app prints one line and uses the local SQLite file, so chat keeps working. Check the service log for "using MySQL".
- Install the driver on the box after the first start has created `.venv`: `.venv/bin/pip install -r requirements-mysql.txt`, then `sudo systemctl restart chatify`.
- Existing SQLite chats are not copied over automatically. Use Export on the old site and Import on the new one.
